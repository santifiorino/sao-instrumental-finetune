import json

def get_custom_metadata(info, audio):

    path = "/content/renders_metadata/" + info["relpath"][:-4] + ".json"
    metadata = open(path, encoding='utf-8')
    metadata = json.load(metadata)

    return {
        "prompt": metadata["prompt"]
    }