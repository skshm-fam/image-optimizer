
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

ALL_IMAGE_EXTS = (".svg", ".webp", ".png", ".jpeg", ".jpg")


def get_large_files(directory):
    files = []
    for root, _, filenames in os.walk(directory):
        for f in filenames:
            if f.lower().endswith(ALL_IMAGE_EXTS):
                path = Path(root) / f
                size = path.stat().st_size
                if size > SIZE_LIMIT:
                    files.append((str(path), size))
    return files


def human_size(size):
    return f"{size/1024:.1f} KB"


def select_files(files, message="Select files (space to toggle)"):
    choices = [
        inquirer.Checkbox(
            "selected",
            message=message,
            choices=[f"{path} ({human_size(size)})" for path, size in files],
        )
    ]
    answers = inquirer.prompt(choices)
    return answers.get("selected", []) if answers else []


def resolve_selected(display_selected, all_files):
    return [path for path, size in all_files if any(path in disp for disp in display_selected)]


def ask_action():
    answer = inquirer.prompt([
        inquirer.List(
            "action",
            message="What do you want to do with the large image files?",
            choices=["optimize", "convert"],
        )
    ])
    return answer["action"] if answer else None


def ask_settings():
    questions = [
        inquirer.Text("quality", message="Quality (0-100)", default="75"),
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


def optimize_avif(path, quality, width, height):
    crf = int((100 - int(quality)) * 63 / 100)
    tmp = path + ".tmp.avif"
    cmd = ["ffmpeg", "-y", "-i", path]
    if width or height:
        w = width if width else "-1"
        h = height if height else "-1"
        cmd += ["-vf", f"scale={w}:{h}"]
    cmd += ["-c:v", "libsvtav1", "-crf", str(crf), tmp]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        os.replace(tmp, path)
        print(f"Optimized AVIF: {path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed AVIF: {path}", e.stderr.decode(errors="replace"))
        if os.path.exists(tmp):
            os.remove(tmp)


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


def convert_image(path, fmt, quality, width, height):
    """Returns the output path on success, None on failure."""
    src = Path(path)
    output = src.with_suffix(f".{fmt}")

    if fmt == "webp":
        cmd = ["cwebp", "-q", str(quality)]
        if width:
            cmd += ["-resize", width, height if height else "0"]
        cmd += [path, "-o", str(output)]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Converted: {path} -> {output}")
            return str(output)
        except subprocess.CalledProcessError:
            pass

    if fmt == "avif":
        # Map quality 0-100 to SVT-AV1 crf 63-0 (lower crf = better quality)
        crf = int((100 - int(quality)) * 63 / 100)
        cmd = ["ffmpeg", "-y", "-i", path]
        if width or height:
            w = width if width else "-1"
            h = height if height else "-1"
            cmd += ["-vf", f"scale={w}:{h}"]
        cmd += ["-c:v", "libsvtav1", "-crf", str(crf), str(output)]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Converted: {path} -> {output}")
            return str(output)
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg failed for {path}: {e.stderr.decode(errors='replace')}")

    # Fallback to Pillow (also handles avif with pillow-avif-plugin)
    try:
        from PIL import Image
        img = Image.open(path)
        if width or height:
            w = int(width) if width else img.width
            h = int(height) if height else img.height
            img = img.resize((w, h), Image.LANCZOS)
        img.save(str(output), quality=int(quality))
        print(f"Converted: {path} -> {output}")
        return str(output)
    except Exception as e:
        print(f"Failed to convert {path}: {e}")
        return None


def main():
    directory = input("Enter directory path: ").strip()

    if not os.path.isdir(directory):
        print("Invalid directory")
        return

    large_files = get_large_files(directory)

    if not large_files:
        print("No image files >50KB found.")
        return

    print(f"\nFound {len(large_files)} image file(s) >50KB.")

    action = ask_action()
    if not action:
        return

    if action == "optimize":
        optimizable = [(p, s) for p, s in large_files if p.lower().endswith((".svg", ".webp"))]
        if not optimizable:
            print("No SVG/WebP files >50KB to optimize.")
            return

        settings = ask_settings()
        quality = int(settings.get("quality", 75))
        width = settings.get("width", "")
        height = settings.get("height", "")

        selected = resolve_selected(
            select_files(optimizable, "Select files to optimize (space to toggle)"),
            optimizable,
        )

        if not selected:
            print("No files selected.")
            return

        print("\nOptimizing...\n")
        for path in selected:
            if path.lower().endswith(".svg"):
                optimize_svg(path)
            elif path.lower().endswith(".webp"):
                optimize_webp(path, quality, width, height)

    elif action == "convert":
        png_jpeg = [(p, s) for p, s in large_files if p.lower().endswith((".png", ".jpeg", ".jpg"))]
        webp_files = [(p, s) for p, s in large_files if p.lower().endswith(".webp")]

        if not png_jpeg and not webp_files:
            print("No PNG/JPEG/WebP files >50KB to convert.")
            return

        generated = []  # collect output paths for the optimization follow-up

        if png_jpeg:
            print(f"\nFound {len(png_jpeg)} PNG/JPEG file(s) >50KB — will convert to WebP.")
            selected_png = resolve_selected(
                select_files(png_jpeg, "Select PNG/JPEG files to convert to WebP"),
                png_jpeg,
            )
            if selected_png:
                print("\nConverting to WebP...\n")
                for path in selected_png:
                    out = convert_image(path, "webp", 75, "", "")
                    if out:
                        generated.append(out)

        if webp_files:
            print(f"\nFound {len(webp_files)} WebP file(s) >50KB — will convert to AVIF.")
            selected_webp = resolve_selected(
                select_files(webp_files, "Select WebP files to convert to AVIF"),
                webp_files,
            )
            if selected_webp:
                print("\nConverting to AVIF...\n")
                for path in selected_webp:
                    out = convert_image(path, "avif", 75, "", "")
                    if out:
                        generated.append(out)

        if generated:
            ans = inquirer.prompt([
                inquirer.Confirm(
                    "optimize",
                    message=f"Optimize the {len(generated)} generated file(s) now?",
                    default=True,
                )
            ])
            if ans and ans["optimize"]:
                settings = ask_settings()
                quality = int(settings.get("quality", 75))
                width = settings.get("width", "")
                height = settings.get("height", "")

                gen_with_sizes = [(p, Path(p).stat().st_size) for p in generated if Path(p).exists()]
                selected_gen = resolve_selected(
                    select_files(gen_with_sizes, "Select generated files to optimize"),
                    gen_with_sizes,
                )

                if selected_gen:
                    print("\nOptimizing...\n")
                    for path in selected_gen:
                        if path.lower().endswith(".webp"):
                            optimize_webp(path, quality, width, height)
                        elif path.lower().endswith(".avif"):
                            optimize_avif(path, quality, width, height)

    print("\nDone!")


if __name__ == "__main__":
    main()
