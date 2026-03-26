
import re
from pathlib import Path

def extract_files_from_response(response_text: str, output_dir: str = "."):
    """
    Extract all files from Claude's response and save them.

    Usage:
        1. Save Claude's response to response.txt
        2. Run: python extract.py
    """
    # Pattern to match our file markers
    pattern = r'▼▼▼ FILE: (.+?) ▼▼▼
(.*?)▲▲▲ END FILE ▲▲▲'

    matches = re.findall(pattern, response_text, re.DOTALL)

    if not matches:
        print("No files found! Make sure the response uses the correct markers.")
        print("Expected format:")
        print("▼▼▼ FILE: path/to/file.py ▼▼▼")
        print("<content>")
        print("▲▲▲ END FILE ▲▲▲")
        return

    output_path = Path(output_dir)
    created_files = []

    for filepath, content in matches:
        filepath = filepath.strip()
        content = content.strip()

        full_path = output_path / filepath

        # Create parent directories
        full_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)

        created_files.append(filepath)
        print(f"✓ {filepath}")

    print(f"\n{'='*50}")
    print(f"Successfully extracted {len(created_files)} files!")
    print(f"{'='*50}")

    # Create data directories
    data_dirs = ['data/chromadb', 'data/logs', 'assets/images/character', 'assets/sounds']
    for d in data_dirs:
        (output_path / d).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {d}")

if __name__ == "__main__":
    import sys

    # Read from file or stdin
    if len(sys.argv) > 1:
        response_file = sys.argv[1]
        with open(response_file, 'r', encoding='utf-8') as f:
            response = f.read()
    else:
        print("Paste Claude's response (press Ctrl+D or Ctrl+Z when done):")
        response = sys.stdin.read()

    extract_files_from_response(response)
