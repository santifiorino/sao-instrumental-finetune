import tempfile
from pathlib import Path

import numpy as np
import soundfile as sf
import pyloudnorm as pyln
from pedalboard.io import AudioFile
from mido import MidiFile

from instruments_map import instruments_map

sample_rate = 44100
num_channels = 2
output_dir = Path("renders")
output_dir.mkdir(parents=True, exist_ok=True)


def main():
    root = Path("clean_midi")
    if not root.exists():
        print("clean_midi directory not found. Exiting...")
        return

    for artist_dir in root.iterdir():
        if not artist_dir.is_dir():
            continue
        for midi_track_dir in artist_dir.iterdir():
            if not midi_track_dir.is_dir():
                continue
            render_song(artist_dir, midi_track_dir)


def render_song(artist_dir, midi_track_dir):
    output_path = output_dir / artist_dir.name / f"{midi_track_dir.name}.wav"

    if output_path.exists():
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f'Rendering "{midi_track_dir.name}" by {artist_dir.name}...')

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)

        synthesize_all_tracks(midi_track_dir, temp_dir)
        mix_and_normalize(temp_dir, output_path)


def synthesize_all_tracks(midi_dir, temp_dir):
    for midi_path in midi_dir.iterdir():
        synthesize_single_track(midi_path, temp_dir)


def synthesize_single_track(midi_path, temp_dir):
    print(f"\tSynthesizing {midi_path.name}...")

    instrument_number = int(midi_path.stem.split("_")[0])
    if instrument_number not in instruments_map:
        print(
            f"\t\tInstrument {instrument_number} not found in instruments_map. Skipping..."
        )
        return

    instrument = instruments_map[instrument_number]
    midi_messages = get_midi_messages(midi_path)

    audio = instrument(
        midi_messages,
        duration=get_midi_duration(midi_path),
        sample_rate=sample_rate,
        num_channels=num_channels,
    )

    audio_path = temp_dir / f"{midi_path.stem}.wav"
    save_audio(audio, audio_path)

    # TODO: VST3 Effects
    print(f"\t\tNormalizing loudness of synthesized audio...")
    normalize_loudness(audio_path.as_posix())


def save_audio(audio, audio_path):
    with AudioFile(audio_path.as_posix(), "w", sample_rate, num_channels) as f:
        f.write(audio)


def mix_and_normalize(temp_dir, output_path):
    print(f"\tMixing all audio files...")
    mix_audio_files(temp_dir, output_path)
    print(f"\t\tNormalizing loudness of mixed audio...")
    normalize_loudness(output_path.as_posix())


def get_midi_messages(file):
    midi_file = MidiFile(file)
    ticks_per_beat = midi_file.ticks_per_beat
    midi_messages = []
    for track in midi_file.tracks:
        time = 0
        for msg in track:
            time += msg.time
            if msg.type in ["note_on", "note_off"]:
                midi_messages.append(
                    (msg.bytes(), ticks_to_seconds(time, 500000, ticks_per_beat))
                )
    return midi_messages


def ticks_to_seconds(ticks, tempo, ticks_per_beat):
    return ticks * tempo / 1e6 / ticks_per_beat


def get_midi_duration(file):
    midi_file = MidiFile(file)
    return midi_file.length


def normalize_loudness(file):
    data, rate = sf.read(file)
    meter = pyln.Meter(rate)
    loudness = meter.integrated_loudness(data)
    loudness_normalized_audio = pyln.normalize.loudness(data, loudness, -12.0)
    sf.write(file, loudness_normalized_audio, rate)


def mix_audio_files(dir, output_path):
    audio_paths = [path for path in dir.iterdir() if path.is_file()]
    audio_files = [sf.read(path.as_posix()) for path in audio_paths]
    wav_datas = [file[0] for file in audio_files]
    wav_rates = [file[1] for file in audio_files]

    # Pad all arrays to the same length
    max_length = max(len(wav_data) for wav_data in wav_datas)

    padded_wav_datas = []
    for wav_data in wav_datas:
        if len(wav_data) < max_length:
            padding = max_length - len(wav_data)
            padded_data = np.pad(wav_data, ((0, padding), (0, 0)), mode="constant")
            padded_wav_datas.append(padded_data)
        else:
            padded_wav_datas.append(wav_data)

    mixed_wav_data = sum(padded_wav_datas)
    mixed_wav_rate = wav_rates[0]
    sf.write(output_path.as_posix(), mixed_wav_data, mixed_wav_rate)


if __name__ == "__main__":
    main()
