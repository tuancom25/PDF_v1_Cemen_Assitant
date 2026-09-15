import json
from pathlib import Path
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("python -m scripts.inspect_page <json_path>")
        return

    path = Path(sys.argv[1])

    if not path.exists():
        print(f"File not found: {path}")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("=" * 70)
    print("PAGE JSON")
    print("=" * 70)

    print(f"File: {path}")
    print()

    print("Top-level keys:")
    for key in data.keys():
        print(f"  - {key}")

    print()
    print("Full JSON:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()