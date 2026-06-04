import json
from pathlib import Path

def convert_json_to_jsonl(input_path: str, output_path: str):
    path = Path(input_path)
    if not path.exists():
        print(f"Error: {input_path} not found.")
        return

    with open(path, "r") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"Error: {input_path} does not contain a JSON list.")
        return

    with open(output_path, "w") as f:
        for entry in data:
            f.write(json.dumps(entry) + "\n")
    
    print(f"Successfully converted {len(data)} events to {output_path}")

if __name__ == "__main__":
    convert_json_to_jsonl(
        "data/outputs/events/events.json",
        "data/outputs/events/events.jsonl"
    )
