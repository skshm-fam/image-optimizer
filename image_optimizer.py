
#!/usr/bin/env python3

import os
import subprocess
from pathlib import Path

try:
    import inquirer
except ImportError:
    print("Install dependency: pip install inquirer")
    exit(1)

SIZE_LIMIT = 50 * 1024  # 50 KB


def get_large_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for f in filenames:
            if f.lower().endswith((".svg", ".webp")):
                path = Path(root) / f
                size = path.stat().st_size
                if size > SIZE_LIMIT:
                    files.append((str(path), size))
    return files


def human_size(size):
    return f"{size/1024:.1f} KB"


def select_files(files):
    choices = [
        inquirer.Checkbox(
            "selected",
            message="Select files to optimize (space to toggle)",
            choices=[f"{path} ({human_size(size)})" for path, size in files],
        )
    ]
    answers = inquirer.prompt(choices)
    return answers.get("selected", []) if answers else []


def ask_settings():
    questions = [
        inquirer.Text("quality", message="WebP Quality (0-100)", default="75"),
        inquirer.Text("width", message="Resize width (or leave blank)", default=""),
        inquirer.Text("height", message="Resize height (or leave blank)", default=""),
    ]
    return inquirer.prompt(questions)


def optimize_svg(path):
    output = path.replace(".svg", ".opt.svg")
    try:
        subprocess.run(["svgo", path, "-o", output], check=True)
        os.replace(output, path)
        print(f"Optimized SVG: {path}")
    except Exception as e:
        print(f"Failed SVG: {path}", e)


def optimize_webp(path, quality, width, height):
    output = path.replace(".webp", ".opt.webp")

    cmd = ["cwebp", "-q", str(quality)]

    if width:
        cmd += ["-resize", width, height if height else "0"]

    cmd += [path, "-o", output]

    try:
        subprocess.run(cmd, check=True)
        os.replace(output, path)
        print(f"Optimized WebP: {path}")
    except Exception as e:
        print(f"Failed WebP: {path}", e)


def main():
    directory = input("Enter directory path: ").strip()

    if not os.path.isdir(directory):
        print("Invalid directory")
        return

    files = get_large_files(directory)

    if not files:
        print("No SVG/WebP files >50KB found")
        return

    selected_display = select_files(files)

    if not selected_display:
        print("No files selected")
        return

    # map back to actual paths
    selected_paths = [
        path for path, size in files
        if any(path in disp for disp in selected_display)
    ]

    settings = ask_settings()
    quality = int(settings.get("quality", 75))
    width = settings.get("width")
    height = settings.get("height")

    print("\nStarting optimization...\n")

    for path in selected_paths:
        if path.endswith(".svg"):
            optimize_svg(path)
        elif path.endswith(".webp"):
            optimize_webp(path, quality, width, height)

    print("\nDone!")


if __name__ == "__main__":
    main()
