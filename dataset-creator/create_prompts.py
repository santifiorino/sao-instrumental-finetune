import json
import random
from pathlib import Path

from litellm import completion
from dotenv import load_dotenv

load_dotenv()

LLM_MODEL = "gemini/gemini-2.5-pro"

base_dir = Path("clean_midi")
output_dir = Path("renders")
system_prompt = Path("system_prompt.md").read_text()


def main():
    for artist_dir in base_dir.iterdir():
        json_paths = list(artist_dir.glob("*.json"))
        for json_path in json_paths:
            json_data = json.loads(json_path.read_text())
            output_path = output_dir / artist_dir.name / f"{json_path.stem}.json"
            if output_path.exists():
                continue

            print(f'Processing "{json_path.name}"...')
            prompt = get_system_prompt()
            response = completion(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": json.dumps(json_data)},
                ],
            )
            generated_prompt = response.choices[0].message.content.strip()
            print(f"\t{generated_prompt}")

            json_data["prompt"] = generated_prompt
            with open(output_path, "w") as f:
                json.dump(json_data, f, indent=2)
            json_path.unlink()


def get_system_prompt():
    tags_md = """**Tags**
A list of words assigned by users to the track.
They often describe **genre, style, and feel**, and are **extremely important.**
* If a genre appears (e.g., "jazz", "rock"), include one or two genres, not all.
* Keep all relevant adjectives describing the mood or feel."""

    acousticness_md = """**Acousticness and Energy**:
Both range from 0 to 1:
* If **acousticness is close to 1**, mention that the track is acoustic.
* If **energy is close to 1**, describe it as energetic.
* If **energy is close to 0**, describe it as chill or quiet."""

    key_md = """**Key, Mode and Tempo**:
Always include the musical key, mode, and BPM somewhere in the paragraph (e.g., "in the key of G Major at 134 BPM")."""

    instruments_md = """**Instruments**:
Always list the instruments present in the audio as part of the description."""

    explanation = [
        tags_md,
        acousticness_md,
        key_md,
        instruments_md,
    ]

    random.shuffle(explanation)

    explanation = [f"{i+1}. {e}\n" for i, e in enumerate(explanation)]
    explanation = "\n".join(explanation)

    return system_prompt.replace("{{explanation}}", explanation)


if __name__ == "__main__":
    main()
