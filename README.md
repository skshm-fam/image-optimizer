
# Image Optimizer CLI

An interactive CLI tool to scan, select, and compress or convert image assets in your project.

---

## Features

* Scans directory recursively
* Filters SVG/WebP files **> 50 KB** for optimization
* Converts PNG/JPEG/JPG/WebP to **WebP** or **AVIF**
* Interactive checkbox file selection
* Custom compression settings (quality, width, height) shared across both workflows
* Uses `svgo` for SVG, `cwebp` for WebP compression, and Pillow as a fallback for conversion

---

## Prerequisites

### Python >= 3.7

```bash
python3 --version
```

### Python dependencies (virtual environment)

Install dependencies into a project-local venv so the script doesn't break when
the system/Homebrew Python changes:

```bash
python3 -m venv .venv
.venv/bin/pip install inquirer pillow
```

Pillow 11.3+ supports AVIF natively — no extra plugin needed.

### ffmpeg (AVIF conversion, optional)

Used first for AVIF encoding (falls back to Pillow if unavailable):

```bash
brew install ffmpeg
```

### SVGO (SVG optimization)

```bash
npm install -g svgo
```

### cwebp (WebP compression/conversion)

#### macOS:

```bash
brew install webp
```

#### Ubuntu/Debian:

```bash
sudo apt install webp
```

---

## Usage

```bash
.venv/bin/python image_optimizer.py
```

Or activate the venv first:

```bash
source .venv/bin/activate
python image_optimizer.py
```

Optional shell alias (add to `~/.zshrc`):

```bash
alias run-img-optimizer="~/build/image_optimizer/.venv/bin/python ~/build/image_optimizer/image_optimizer.py"
```

---

## Workflow

### 1. Enter directory path

```
Enter directory path: /Users/yourname/project/assets
```

### 2. Select SVG/WebP files to optimize (> 50 KB)

If any files over 50 KB are found, a checkbox list appears.

* **↑ / ↓** — navigate
* **SPACE** — select/deselect
* **ENTER** — confirm

If none are found, this step is skipped automatically.

### 3. Enter compression settings

These settings apply to both optimization and conversion:

* **Quality** (0–100, default 75) — compression level
* **Width** — resize width in px, leave blank to skip
* **Height** — resize height in px, leave blank to auto-scale

### 4. Optimization runs

* SVG → optimized with `svgo`
* WebP → re-compressed with `cwebp`

Files are replaced in-place.

### 5. Convert PNG/JPEG/JPG/WebP files

All matching files in the directory are listed. You are asked:

```
Convert PNG/JPEG/JPG/WebP files to
  > webp
    avif
    none (skip)
```

Select files via checkbox, then conversion runs using the quality/width/height from step 3.

**Note:** If you select **webp**, any `.webp` files already in WebP format are automatically skipped. If you select **avif**, `.webp` files are included and converted.

---

## Example

```
Enter directory path: /assets/images

[Select SVG/WebP files > 50KB with SPACE]

Quality: 75
Width: 512
Height:

Starting optimization...
Optimized WebP: /assets/images/banner.webp

Found 4 PNG/JPEG/JPG/WebP file(s).
Convert to: avif

[Select files with SPACE]

Converting to AVIF...
Converted: /assets/images/icon.png -> /assets/images/icon.avif
Converted: /assets/images/hero.jpg -> /assets/images/hero.avif

Done!
```

---

## Troubleshooting

**`svgo: command not found`**
```bash
npm install -g svgo
```

**`cwebp: command not found`**
```bash
brew install webp   # macOS
sudo apt install webp   # Ubuntu
```

**`Install dependency: pip install inquirer`** / **`No module named inquirer`**

You're running a Python that doesn't have the dependencies (e.g. after a Homebrew
Python upgrade). Run via the venv, or recreate it:
```bash
rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install inquirer pillow
```

**AVIF conversion fails**
```bash
brew install ffmpeg
.venv/bin/pip install -U pillow   # Pillow 11.3+ has built-in AVIF
```

---

## Notes

* Original files are overwritten — back them up if needed
* WebP/AVIF compression is lossy when quality < 100
* Resizing gives the largest file size reduction
