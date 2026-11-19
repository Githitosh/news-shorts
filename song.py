#!/usr/bin/env python3
"""Make assets/untitled_song.m4a from assets/midi/untitled_song.mid.

    python song.py

Needs mido, numpy and scipy (pip), FluidSynth with the FluidR3 GM SoundFont, and ffmpeg
(apt install fluidsynth fluid-soundfont-gm ffmpeg).

The MIDI file is 8 bars at 90 BPM (21.33 s) with its parts on one channel and no instruments. Chords play
on a piano, Bass on a fingered bass and Drums on the drum channel. The song is played six times; one
8-bar loop is cut from the third time through, where the reverb and the release of the time before are
already sounding, and the file holds that loop three times (64 s). The cut falls 42 ms before a downbeat
and crossfades into what came just before it, so the song repeats without a seam. At 48 kHz one loop is
exactly 1000 AAC frames, so the pages can repeat it in an MP4 by taking frames again from one loop earlier.
Loudness is about -16 LUFS.
"""
import subprocess
import tempfile
from pathlib import Path

import mido
import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parent
MIDI = ROOT / "assets" / "midi" / "untitled_song.mid"
OUT = ROOT / "assets" / "untitled_song.m4a"
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
RATE = 48000
LOOP_TICKS = 4096        # 8 bars of 4/4 at 128 ticks per beat
N = 1024000              # 8 bars at 90 BPM in samples at 48 kHz
PARTS = {"Chords": (0, 0), "Bass": (1, 33), "Drums": (9, None)}  # channel, General MIDI program


def repeated(src: Path, dst: Path, reps: int) -> None:
    m = mido.MidiFile(src)
    out = mido.MidiFile(type=1, ticks_per_beat=m.ticks_per_beat)
    for t in m.tracks:
        part = next((k for k in PARTS if t.name.startswith(k)), None)
        if part is None:
            continue
        ch, prog = PARTS[part]
        meta, ev, tick = [], [], 0
        for msg in t:
            tick += msg.time
            if msg.is_meta:
                if msg.type in ("set_tempo", "time_signature", "track_name") and tick == 0:
                    meta.append(msg.copy(time=0))
            elif msg.type in ("note_on", "note_off"):
                ev.append((tick, msg))
        notes = []
        for r in range(reps):
            for tk, msg in ev:
                on = msg.type == "note_on" and msg.velocity > 0
                notes.append((r * LOOP_TICKS + tk, 1 if on else 0, msg.copy(channel=ch, time=0)))
        notes.sort(key=lambda x: (x[0], x[1]))  # a note-off before a note-on at the same tick
        tr = mido.MidiTrack()
        tr.extend(meta)
        if prog is not None:
            tr.append(mido.Message("program_change", channel=ch, program=prog, time=0))
        tr.append(mido.Message("control_change", channel=ch, control=7, value=100 if part == "Drums" else 110, time=0))
        last = 0
        for tk, _, msg in notes:
            tr.append(msg.copy(time=tk - last))
            last = tk
        tr.append(mido.MetaMessage("end_of_track", time=reps * LOOP_TICKS + 512 - last))
        out.tracks.append(tr)
    out.save(dst)


def run(*cmd: str) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        repeated(MIDI, tmp / "rep.mid", 6)
        run("fluidsynth", "-ni", "-q", "-r", str(RATE), "-g", "0.6", "-F", str(tmp / "rep.wav"), SF2, str(tmp / "rep.mid"))
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp / "rep.wav"),
            "-af", "volume=6.4dB,alimiter=limit=0.74:attack=4:release=60:level=false", "-c:a", "pcm_f32le", str(tmp / "lim.wav"))
        rate, x = wavfile.read(tmp / "lim.wav")
        assert rate == RATE
        x = x.astype(np.float64)
        pre, fade = 2000, 1500
        a = 2 * N - pre
        seg = x[a:a + N].copy()
        t = (np.arange(fade) + 0.5) / fade
        seg[N - fade:] = x[a + N - fade:a + N] * np.cos(t * np.pi / 2)[:, None] + x[a - fade:a] * np.sin(t * np.pi / 2)[:, None]
        seg = np.roll(seg, -pre, axis=0)  # the file starts on the downbeat
        wavfile.write(tmp / "loop.wav", RATE, np.tile(seg, (3, 1)).astype(np.float32))
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp / "loop.wav"),
            "-c:a", "aac", "-b:a", "128k", "-ar", str(RATE), "-movflags", "+faststart", str(OUT))
    print(f"{OUT.relative_to(ROOT)} {OUT.stat().st_size / 1048576:.2f} MB")


if __name__ == "__main__":
    main()
