# Dataset Creator

## 1. Installation

Create a virtual environment and install the dependencies:

```bash
/dataset-creator $ python -m venv venv
/dataset-creator $ source venv/bin/activate
(venv) /dataset-creator $ pip install -r requirements.txt
```

## 2. Set up the MIDI dataset

### Custom dataset

You can use your own dataset. However, to run the rendering script, it must follow this directory structure:
* A directory named `clean_midi`
* Inside `clean_midi`, one or more directories named after the artist (the artist name is not used during rendering, so you may also use a single directory)
* Inside each artist directory, one directory per song
* Each song directory must contain the MIDI tracks for that song, named with the prefix `[Instrument Code]_`, following the [MIDI Instrument Codes](https://www.ccarh.org/courses/253/handout/gminstruments/)

### Lakh MIDI Dataset

If you want to follow our process:
1. Download the [Lakh MIDI Dataset v0.1](https://colinraffel.com/projects/lmd/) (Clean MIDI subset)
2. Run the MIDI cleaning script (removes duplicates and corrupt files, and splits MIDIs by track):
```bash
(venv) /dataset-creator $ python clean_lakh_dataset.py
```
3. Add the API keys for [Spotify](https://developer.spotify.com/documentation/web-api) and [LastFM](https://www.last.fm/api) to `.env`, then run the metadata generation script (looks up the songs on the APIs and generates a .json with the metadata):
```
(venv) /dataset-creator $ python create_json_metadata
```
4. Add the API key for your LLM of choice to `.env`set the model in the `LLM_MODEL` variable in `create_prompts.py`, and run the script (it calls the LLM for each `.json` file and converts the output into a prompt):
```bash
(venv) /dataset-creator $ python create_prompts.py
```

## 2. Add the VST3 Instruments

1. Place your VST3 instruments in the `/instruments` directory..
2. If you want to use an instrument with a custom preset, save the preset in the `/presets` directory. This is useful if you want to use the same VST3i with different configurations to render different instrument codes.
3. Fill in the `instrument code -> instrument` mapping in `instruments_map.py`, where:
    * `instrument code` is an integer, following the [MIDI Instrument Codes](https://www.ccarh.org/courses/253/handout/gminstruments/)
    * `instrument` is the VST3i used to render MIDI tracks with that code

## 3. Run the rendering script

Run the script to start rendering your songs into the `render` directory.

```bash
(venv) /dataset-creator $ python render_songs.py
```