# MIDI Parser Implementation Notes

## Format Overview

Standard MIDI File (SMF) format consists of:
1. **Header chunk** (`MThd`) — file type, track count, timing
2. **Track chunks** (`MTrk`) — sequence of MIDI events

## Header Chunk

```
Offset  Size  Description
0       4     Chunk type: "MThd"
4       4     Chunk length: always 6
8       2     Format: 0=single, 1=multi-sync, 2=multi-async
10      2     Number of tracks
12      2     Division (ticks per quarter note, or SMPTE)
```

## Variable-Length Quantity (VLQ)

Delta times use VLQ encoding — each byte uses 7 bits of data,
with the MSB indicating continuation:

```typescript
function readVLQ(buffer: Uint8Array, offset: number): [number, number] {
  let value = 0;
  let bytesRead = 0;
  let byte: number;

  do {
    byte = buffer[offset + bytesRead];
    value = (value << 7) | (byte & 0x7F);
    bytesRead++;
  } while (byte & 0x80);

  return [value, bytesRead];
}
```

## Event Types

| Status Byte | Event Type | Data Bytes |
|-------------|------------|------------|
| 0x80–0x8F | Note Off | note, velocity |
| 0x90–0x9F | Note On | note, velocity |
| 0xA0–0xAF | Aftertouch | note, pressure |
| 0xB0–0xBF | Control Change | controller, value |
| 0xC0–0xCF | Program Change | program |
| 0xD0–0xDF | Channel Pressure | pressure |
| 0xE0–0xEF | Pitch Bend | LSB, MSB |
| 0xFF | Meta Event | type, length, data |

## Tempo Meta Event (0xFF 0x51)

```typescript
function parseTempo(data: Uint8Array): number {
  // 3 bytes, microseconds per quarter note
  return (data[0] << 16) | (data[1] << 8) | data[2];
}

function bpm(microsecondsPerBeat: number): number {
  return 60_000_000 / microsecondsPerBeat;
}
```
