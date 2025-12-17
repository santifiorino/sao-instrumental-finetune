import re
from pathlib import Path
import pretty_midi


def remove_duplicates(base_dir: Path) -> None:
    for artist_dir in base_dir.iterdir():
        if not artist_dir.is_dir():
            continue

        songs = list(artist_dir.iterdir())
        for song_path in songs:
            song = song_path.name
            if re.search(r"\.\d", song) is not None:
                duplicated_path = song_path
                original_name = ".".join(song.split(".")[:-2])
                original_path = artist_dir / f"{original_name}.mid"
                if original_path.is_file():
                    # If can't load the original, just remove it and keep the duplicated
                    try:
                        original_midi = pretty_midi.PrettyMIDI(str(original_path))
                    except:
                        original_path.unlink()
                        duplicated_path.rename(original_path)
                        continue
                    # If can't load the duplicated, just remove it and keep the original
                    try:
                        duplicated_midi = pretty_midi.PrettyMIDI(str(duplicated_path))
                    except:
                        duplicated_path.unlink()
                        continue
                    # If can load both, keep the one with more instruments
                    if len(original_midi.instruments) >= len(
                        duplicated_midi.instruments
                    ):
                        duplicated_path.unlink()
                    else:
                        original_path.unlink()
                        duplicated_path.rename(original_path)


def split_midi_by_instrument(base_dir: Path) -> None:
    for artist_dir in base_dir.iterdir():
        if not artist_dir.is_dir():
            continue

        midi_files = [f for f in artist_dir.iterdir() if f.suffix == ".mid"]
        for song_path in midi_files:
            try:
                midi_data = pretty_midi.PrettyMIDI(str(song_path))
            except:
                # If can't load the MIDI file, remove it
                song_path.unlink()
                continue

            song_dir = artist_dir / song_path.stem
            song_dir.mkdir(exist_ok=True)

            for instrument in midi_data.instruments:
                new_midi = pretty_midi.PrettyMIDI()
                new_midi.instruments.append(instrument)
                instrument_name = instrument.name.rstrip()
                instrument_path = (
                    song_dir / f"{instrument.program}_{instrument_name}.mid"
                )
                new_midi.write(str(instrument_path))

            song_path.unlink()


def cleanup_empty_directories(base_dir: Path) -> None:
    for artist_dir in base_dir.iterdir():
        if artist_dir.is_dir() and not any(artist_dir.iterdir()):
            artist_dir.rmdir()


def main():
    base_dir = Path("clean_midi")

    print("Lowercasing filenames and removing duplicates...")
    remove_duplicates(base_dir)

    print("Splitting MIDI files by instrument...")
    split_midi_by_instrument(base_dir)

    print("Cleaning up empty directories...")
    cleanup_empty_directories(base_dir)

    print("Done!")


if __name__ == "__main__":
    main()
