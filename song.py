#!/usr/bin/env python3
"""Make assets/song_1.m4a, song_2.m4a and song_3.m4a from assets/midi/1.mid, 2.mid and 3.mid.

    python song.py          # all three
    python song.py 3        # one of them

Needs mido, numpy and scipy (pip), FluidSynth with the FluidR3 GM SoundFont, and ffmpeg
(apt install fluidsynth fluid-soundfont-gm ffmpeg).

Each MIDI file is 8 bars (1 and 3 at 90 BPM, 21.33 s; 2 at 110 BPM, 17.45 s) with its parts on one channel
and no instruments. Chords play
on a piano, Bass on a fingered bass and Drums on the drum channel. The song is played six times; one
8-bar loop is cut from the third time through, where the reverb and the release of the time before are
already sounding, and the file holds that loop twice. The cut falls 42 ms before a downbeat and
crossfades into what came just before it, so the song repeats without a seam. One loop is made a whole
number of AAC frames at 48 kHz (1000 for 1 and 3; 818 for 2, whose tempo moves by 0.02% for it), so the
pages can repeat it in an MP4 by taking frames again from one loop earlier.
Loudness is about -16 LUFS.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import mido
import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parent
SONGS = ("1", "2", "3")
COPIES = 2               # loops in each file
TARGET = -16.0           # LUFS
SF2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
RATE = 48000
LOOP_TICKS = 4096        # 8 bars of 4/4 at 128 ticks per beat
PARTS = {"Chords": (0, 0), "Bass": (1, 33), "Drums": (9, None)}  # channel, General MIDI program


def loop_frames(src: Path) -> int:
    """One loop in whole AAC frames (1024 samples at 48 kHz)."""
    m = mido.MidiFile(src)
    tempo = next((msg.tempo for t in m.tracks for msg in t if msg.type == "set_tempo"), 500000)
    beats = LOOP_TICKS / m.ticks_per_beat
    return round(beats * tempo / 1e6 * RATE / 1024)


def repeated(src: Path, dst: Path, reps: int, frames: int) -> None:
    m = mido.MidiFile(src)
    tempo = round(frames * 1024 / RATE / (LOOP_TICKS / m.ticks_per_beat) * 1e6)  # the loop fits the frames
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
                if msg.type == "set_tempo" and tick == 0:
                    meta.append(msg.copy(tempo=tempo, time=0))
                elif msg.type in ("time_signature", "track_name") and tick == 0:
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


def lufs(path: Path) -> float:
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, check=True)
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])


def make(name: str) -> None:
    midi = ROOT / "assets" / "midi" / f"{name}.mid"
    out = ROOT / "assets" / f"song_{name}.m4a"
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        frames = loop_frames(midi)
        N = frames * 1024
        repeated(midi, tmp / "rep.mid", 6, frames)
        run("fluidsynth", "-ni", "-q", "-r", str(RATE), "-g", "0.6", "-F", str(tmp / "rep.wav"), SF2, str(tmp / "rep.mid"))
        gain = TARGET - lufs(tmp / "rep.wav") + 0.4   # the limiter takes off a little
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp / "rep.wav"),
            "-af", f"volume={gain:.2f}dB,alimiter=limit=0.68:attack=4:release=60:level=false", "-c:a", "pcm_f32le", str(tmp / "lim.wav"))
        rate, x = wavfile.read(tmp / "lim.wav")
        assert rate == RATE
        x = x.astype(np.float64)
        pre, fade = 2000, 1500
        a = 2 * N - pre
        seg = x[a:a + N].copy()
        t = (np.arange(fade) + 0.5) / fade
        seg[N - fade:] = x[a + N - fade:a + N] * np.cos(t * np.pi / 2)[:, None] + x[a - fade:a] * np.sin(t * np.pi / 2)[:, None]
        seg = np.roll(seg, -pre, axis=0)  # the file starts on the downbeat
        wavfile.write(tmp / "loop.wav", RATE, np.tile(seg, (COPIES, 1)).astype(np.float32))
        run("ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(tmp / "loop.wav"),
            "-c:a", "aac", "-b:a", "128k", "-ar", str(RATE), "-movflags", "+faststart", str(out))
    print(f"{out.relative_to(ROOT)} {out.stat().st_size / 1048576:.2f} MB, {lufs(out):.1f} LUFS, loop {frames} frames ({N / RATE:.3f} s)")


def main() -> None:
    for name in sys.argv[1:] or SONGS:
        make(name)


if __name__ == "__main__":
    main()
