import os
import json
from pathlib import Path
import pylast
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from dotenv import load_dotenv

load_dotenv()

KEY_DICT = {
    -1: "",
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}

MODE_DICT = {0: "Minor", 1: "Major"}

network = pylast.LastFMNetwork(
    api_key=os.getenv("LASTFM_API_KEY"),
    api_secret=os.getenv("LASTFM_API_SECRET"),
    username=os.getenv("LASTFM_USERNAME"),
    password_hash=pylast.md5(os.getenv("LASTFM_PASSWORD")),
)

auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIFY_API_KEY"),
    client_secret=os.getenv("SPOTIFY_API_SECRET"),
)
sp = spotipy.Spotify(auth_manager=auth_manager)


def fetch_metadata(base_dir: Path, lastfm_network, spotify_client) -> None:
    for artist_dir in base_dir.iterdir():
        if not artist_dir.is_dir():
            continue

        for song_dir in artist_dir.iterdir():
            if not song_dir.is_dir():
                continue

            # Fetch Last.fm metadata
            matched_search = lastfm_network.search_for_track(
                artist_dir.name, song_dir.name
            )
            # If can't find the song on Last.fm, remove it
            if int(matched_search.get_total_result_count()) == 0:
                song_dir.rmdir()
                continue

            best_match = matched_search.get_next_page()[0]
            tags = best_match.get_top_tags()
            metadata = {
                "Song": best_match.get_name(),
                "Artist": best_match.get_artist().get_name(),
                "Tags": [tag.item.get_name() for tag in tags],
            }

            # Fetch Spotify metadata
            search_result = spotify_client.search(
                metadata["Artist"] + " " + metadata["Song"], limit=1, type="track"
            )
            if len(search_result["tracks"]["items"]) == 0:
                song_dir.rmdir()
                continue

            track_id = search_result["tracks"]["items"][0]["id"]
            spotify_features = spotify_client.audio_features([track_id])[0]
            metadata.update(
                {
                    "duration_ms": spotify_features["duration_ms"],
                    "acousticness": spotify_features["acousticness"],
                    "danceability": spotify_features["danceability"],
                    "energy": spotify_features["energy"],
                }
            )

            spotify_analysis = spotify_client.audio_analysis(track_id)
            metadata.update(
                {
                    "key": KEY_DICT[spotify_analysis["track"]["key"]],
                    "mode": MODE_DICT[spotify_analysis["track"]["mode"]],
                    "tempo": spotify_analysis["track"]["tempo"],
                    "sections": spotify_analysis["sections"],
                }
            )

            # Save combined metadata
            json_path = song_dir / "metadata.json"
            with open(json_path, "w") as json_file:
                json.dump(metadata, json_file)


def main():
    base_dir = Path("clean_midi")

    print("Fetching metadata from Last.fm and Spotify...")
    fetch_metadata(base_dir, network, sp)

    print("Done!")


if __name__ == "__main__":
    main()
