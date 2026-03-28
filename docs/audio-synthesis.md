# Audio Synthesis Engine

## Overview

The Fate Symphony audio synthesis engine generates orchestral audio from MIDI-like event sequences using physical modeling and sample-based synthesis.

## Architecture

```
Event Sequence → Scheduler → Voice Allocator → Synthesis Engine → Mixer → Output
                                                      ↓
                                            ┌─────────────────┐
                                            │  Synthesis Types │
                                            │  ├─ Sample-based │
                                            │  ├─ FM Synthesis │
                                            │  └─ Physical Model│
                                            └─────────────────┘
```

## Voice Allocation

```typescript
interface Voice {
  id: number;
  noteOn: boolean;
  pitch: number;
  velocity: number;
  instrument: InstrumentType;
  startTime: number;
  envelope: ADSREnvelope;
}

class VoiceAllocator {
  private voices: Voice[] = new Array(64).fill(null).map((_, i) => ({
    id: i, noteOn: false, pitch: 0, velocity: 0,
    instrument: 'piano', startTime: 0,
    envelope: { attack: 0.01, decay: 0.1, sustain: 0.7, release: 0.3 }
  }));

  allocate(pitch: number, velocity: number, instrument: InstrumentType): Voice {
    // Find free voice, or steal oldest active voice
    const free = this.voices.find(v => !v.noteOn);
    if (free) return this.activate(free, pitch, velocity, instrument);

    const oldest = this.voices.reduce((a, b) =>
      a.startTime < b.startTime ? a : b
    );
    return this.activate(oldest, pitch, velocity, instrument);
  }
}
```

## ADSR Envelope

```typescript
class ADSREnvelope {
  constructor(
    private attack: number,   // seconds
    private decay: number,    // seconds
    private sustain: number,  // 0.0–1.0
    private release: number   // seconds
  ) {}

  amplitude(t: number, noteOff: number | null): number {
    if (t < this.attack) return t / this.attack;
    if (t < this.attack + this.decay)
      return 1.0 - (1.0 - this.sustain) * (t - this.attack) / this.decay;
    if (noteOff === null) return this.sustain;
    const releaseT = t - noteOff;
    return Math.max(0, this.sustain * (1 - releaseT / this.release));
  }
}
```

## Reverb (Schroeder Algorithm)

```typescript
class SchroederReverb {
  private combFilters: CombFilter[];
  private allpassFilters: AllpassFilter[];

  constructor(roomSize: number = 0.5, damping: number = 0.5) {
    // 4 comb filters in parallel
    const delays = [1557, 1617, 1491, 1422]; // samples at 44.1kHz
    this.combFilters = delays.map(d => new CombFilter(d, roomSize, damping));
    // 2 allpass filters in series
    this.allpassFilters = [
      new AllpassFilter(225, 0.5),
      new AllpassFilter(556, 0.5)
    ];
  }

  process(input: Float32Array): Float32Array {
    const wet = this.combFilters.reduce(
      (acc, cf) => add(acc, cf.process(input)),
      new Float32Array(input.length)
    );
    return this.allpassFilters.reduce((sig, ap) => ap.process(sig), wet);
  }
}
```

## Performance Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| Latency | < 10ms | 6.2ms |
| Polyphony | 64 voices | 64 voices |
| Sample rate | 44.1kHz | 44.1kHz |
| CPU usage | < 15% | 11.3% |
| Memory | < 256MB | 187MB |
