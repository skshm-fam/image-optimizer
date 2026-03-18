
# 📦 Image Optimizer CLI (SVG + WebP)

A simple interactive CLI tool to scan, select, and compress large `.svg` and `.webp` assets in your project.

---

## 🚀 Features

* 🔍 Scans directory recursively
* 📏 Filters only images **> 50 KB**
* ✅ Interactive checkbox selection (space to toggle)
* ⚙️ Custom compression settings:

  * WebP quality
  * Resize width / height
* 🛠 Uses:

  * `svgo` for SVG optimization
  * `cwebp` for WebP compression

---

## 🧰 Prerequisites

Make sure you have the following installed:

### 1. Python (>= 3.7)

Check:

```bash
python3 --version
```

---

### 2. Install Python dependency

```bash
pip install inquirer
```

---

### 3. Install SVGO (for SVG optimization)

```bash
npm install -g svgo
```

Check:

```bash
svgo --version
```

---

### 4. Install WebP tools (`cwebp`)

#### macOS (Homebrew):

```bash
brew install webp
```

#### Ubuntu/Debian:

```bash
sudo apt install webp
```

#### Verify:

```bash
cwebp -version
```

---

## 📁 Setup

1. Save the script as:

```
image_optimizer.py
```

2. Give execution permission (optional):

```bash
chmod +x image_optimizer.py
```

---

## ▶️ Running the Script

```bash
python image_optimizer.py
```

---

## 🧭 Step-by-Step Usage

### 1. Enter directory path

Example:

```
/Users/yourname/project/assets
```

---

### 2. Select files to optimize

* Use **↑ / ↓ arrow keys** to navigate
* Press **SPACE** to select/deselect
* Press **ENTER** to confirm

---

### 3. Enter compression settings

You’ll be prompted for:

#### 🔸 WebP Quality

* Range: `0–100`
* Recommended: `70–75`

#### 🔸 Resize Width (optional)

* Example: `512`
* Leave blank to skip

#### 🔸 Resize Height (optional)

* Example: `512`
* Leave blank to auto-scale

---

### 4. Optimization starts

* SVG → optimized using `svgo`
* WebP → compressed using `cwebp`

Files are **replaced in-place**

---

## ⚠️ Important Notes

* ⚠️ Original files are overwritten
* SVG optimization depends on structure (some may not shrink much)
* WebP compression is **lossy** if quality < 100
* Resize is optional but gives biggest size reduction

---

## 💡 Tips

* Use `quality = 70` for best balance
* Resize oversized images (huge impact)
* Run this on your entire asset folder before release

---

## 🧪 Example Workflow

```bash
python image_optimizer.py
```

```
Enter directory path:
/assets/images

[Select files with SPACE]

WebP Quality: 75
Width: 512
Height:

→ Optimization complete ✅
```

---

## 🛠 Troubleshooting

### ❌ `svgo: command not found`

```bash
npm install -g svgo
```

---

### ❌ `cwebp: command not found`

Install WebP tools:

```bash
brew install webp
```

---

### ❌ `No module named inquirer`

```bash
pip install inquirer
```

---

## 🔥 Future Improvements (optional)

* Auto-compress until file < 50 KB
* Backup originals before replacing
* Parallel processing for speed
* Git pre-commit hook integration

---

## 👌 You're good to go

Run it on your Flutter assets and you should see **significant size reduction immediately**.
