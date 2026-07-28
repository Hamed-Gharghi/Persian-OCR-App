# Persian OCR App 🇮🇷🖼️🔍📝

[![GitHub stars](https://img.shields.io/github/stars/Hamed-Gharghi/Persian-OCR-App?style=social)](https://github.com/Hamed-Gharghi/Persian-OCR-App/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Hamed-Gharghi/Persian-OCR-App)](https://github.com/Hamed-Gharghi/Persian-OCR-App/issues)
[![GitHub forks](https://img.shields.io/github/forks/Hamed-Gharghi/Persian-OCR-App?style=social)](https://github.com/Hamed-Gharghi/Persian-OCR-App/network/members)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
![Version](https://img.shields.io/badge/Version-1.7.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flet](https://img.shields.io/badge/Flet-0.85%2B-purple)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows&logoColor=white)

**By [Hamed Gharghi](https://github.com/Hamed-Gharghi)** · [Persian-OCR-App](https://github.com/Hamed-Gharghi/Persian-OCR-App)

---

> **Persian OCR App v1.7** — Convert Persian (Farsi) images and PDFs to editable text using **RapidOCR** (ONNX Runtime) and Flet. Includes global screen snip (`Win+Shift+D`) that OCRs a region and types the text into the focused app.
>
> **برنامه OCR فارسی نسخه ۱.۷** — تبدیل عکس و PDF فارسی به متن قابل ویرایش با **RapidOCR** (ONNX Runtime) و Flet. دارای برش صفحه سراسری (`Win+Shift+D`) که ناحیه انتخاب‌شده را OCR می‌کند و متن را در برنامه فعال تایپ می‌کند.

---

## 🪟 Download for Windows

**No installation or Python required!**

- Download the latest ready-to-use Windows executable (`PersianOCR.exe`) from the [Releases page](https://github.com/Hamed-Gharghi/Persian-OCR-App/releases).
- Just download, double-click, and start using Persian OCR on Windows.
- The `.exe` is standalone and much smaller than EasyOCR/PyTorch builds (~target ~200 MB) because OCR runs on **onnxruntime** mobile models.
- **Users do not install RapidOCR separately.** `build_exe.bat` packs RapidOCR, onnxruntime, and the Arabic/English ONNX weights into the exe for offline use.
- The build script downloads/copies models into `rapidocr_models\` automatically on first build (needs internet once).

---

## 🪟 دانلود برای ویندوز

**بدون نیاز به نصب یا پایتون!**

- آخرین نسخه اجرایی ویندوز (`PersianOCR.exe`) را از [صفحه انتشارها](https://github.com/Hamed-Gharghi/Persian-OCR-App/releases) دانلود کنید.
- فقط دانلود کنید، دوبار کلیک کنید و بلافاصله از برنامه OCR فارسی روی ویندوز استفاده کنید.
- فایل اجرایی مستقل است و به‌خاطر RapidOCR/ONNX بسیار سبک‌تر از بیلدهای EasyOCR/PyTorch است.
- **کاربر نیازی به نصب جداگانه RapidOCR ندارد**؛ کتابخانه و مدل‌های ONNX داخل `.exe` بسته‌بندی می‌شوند.
- اسکریپت بیلد مدل‌ها را در `rapidocr_models\` آماده می‌کند (اولین بیلد ممکن است نیاز به اینترنت داشته باشد).

---

## 📑 Navigation | ناوبری

- [🇬🇧 English](#english)
- [🇮🇷 فارسی](#persian)

---

<a name="english"></a>
# 🇬🇧 English

## 🔑 Key Features

- **Persian (Farsi) OCR** — Extract text from Persian images and PDFs via [RapidOCR](https://github.com/RapidAI/RapidOCR) (ONNX Runtime)
- **Fast / Accurate mode** — Smaller vs larger preprocess scale for speed or quality
- **Modern desktop UI** — Built with [Flet](https://flet.dev/) (v0.85+), dark theme, native RTL for Persian
- **Easy to use** — Drag-and-drop (Windows), file picker, or batch folder processing
- **PDF & image support** — PNG, JPG, BMP, and PDF with per-page progress
- **Export formats** — Plain text (`.txt`), Word (`.docx`), and PDF
- **Persian text cleanup** — Normalizes common OCR character errors (ي→ی, ك→ک, …)
- **Screen snip & type** — Press `Win+Shift+D` (or `Ctrl+Shift+D`) anywhere to crop a screen region, run OCR, and auto-type the text into the focused application
- **Saved settings** — Language, speed/accuracy mode, and export format persist between sessions
- **Keyboard shortcuts** — `Ctrl+O` open · `Ctrl+C` copy · `Ctrl+S` save · `Win+Shift+D` screen snip
- **No separate OCR install for end users** — RapidOCR + ONNX models ship inside the exe when you build with `build_exe.bat`
- **No Tesseract / PyTorch install**
- **Bilingual UI** — Switch between English and Persian

---

## 🚀 Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Hamed-Gharghi/Persian-OCR-App.git
   cd Persian-OCR-App
   ```

2. **Install Python 3.10+** (recommended: 3.10, 3.11, or 3.12)

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app:**

   ```bash
   python main.py
   ```

---

## 🖼️ Screenshots | اسکرین‌شات

<p align="center">
  <img src="https://github.com/Hamed-Gharghi/Persian-OCR-App/blob/main/assets/image.png?raw=true" alt="Persian OCR App Screenshot" />
</p>

---

## ❓ What is Persian OCR?

Persian OCR (Optical Character Recognition) converts scanned Persian (Farsi) documents, images, or PDFs into editable and searchable text. This app makes it easy to extract Persian text on your computer without sending data anywhere.

---

<a name="persian"></a>
# 🇮🇷 فارسی

## 🚀 شروع سریع

۱. **کلون کردن مخزن:**

   ```bash
   git clone https://github.com/Hamed-Gharghi/Persian-OCR-App.git
   cd Persian-OCR-App
   ```

۲. **نصب پایتون ۳.۱۰ یا بالاتر** (پیشنهادی: ۳.۱۰، ۳.۱۱ یا ۳.۱۲)

۳. **نصب وابستگی‌ها:**

   ```bash
   pip install -r requirements.txt
   ```

۴. **اجرای برنامه:**

   ```bash
   python main.py
   ```

## ✨ ویژگی‌ها

- 🖥️ رابط کاربری مدرن با Flet (تم تیره، پشتیبانی RTL)
- 🌐 رابط کاربری فارسی و انگلیسی (قابل تغییر)
- 📂 کشیدن و رها کردن فایل، انتخاب فایل، یا پردازش دسته‌ای پوشه
- 🖼️ پیش‌نمایش تصویر/PDF
- 🧠 موتور RapidOCR (ONNX) برای تشخیص متن فارسی بدون PyTorch
- ⚡ حالت سریع یا دقیق (مقیاس پیش‌پردازش)
- ✂️ برش صفحه و تایپ زنده — با `Win+Shift+D` (یا `Ctrl+Shift+D`) بخشی از صفحه را انتخاب کنید؛ متن استخراج و در برنامه فعال تایپ می‌شود
- 💾 خروجی در فرمت txt، docx و pdf
- ⌨️ میانبرهای Ctrl+O / Ctrl+C / Ctrl+S / Win+Shift+D
- 💾 ذخیره تنظیمات بین اجراها

## 📝 نکات

- 🧠 برنامه از **RapidOCR + onnxruntime** استفاده می‌کند (اولین اجرا از سورس ممکن است مدل‌ها را دانلود کند).
- 📄 فایل `settings.json` کنار برنامه (یا کنار `.exe`) برای ذخیره تنظیمات ساخته می‌شود.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a pull request.

---

## ❓ FAQ / Troubleshooting

**Q: Why is the OCR not accurate for some images?**

- Accuracy still depends on image quality. Prefer high-resolution, well-lit, straight scans. RapidOCR is fast and light; tiny/blurry text can still fail.

**Q: First launch is slow / downloads something?**

- Release builds bundle ONNX models via `build_exe.bat`. Developers running from source may download models once into the RapidOCR package `models/` folder.

**Q: PDF OCR fails with a Poppler error?**

- Older builds used `pdf2image`, which required Poppler. Current builds use **PyMuPDF** — no Poppler install is needed.

**Q: Does drag-and-drop work on Linux or macOS?**

- Drag-and-drop onto the window is supported on **Windows** only (`windnd`). On other platforms, use the file picker or **Process Folder**.

---

## 🛠️ Build a single Windows `.exe`

The release build packs Python, Flet, PyMuPDF, OpenCV, and **RapidOCR/onnxruntime** (no PyTorch). Expect a much smaller executable than EasyOCR builds.

1. Test from source:

   ```bat
   pip install -r requirements.txt
   python main.py
   ```

2. Build:

   ```bat
   .\build_exe.bat
   ```

3. Output: `dist\PersianOCR.exe`

### Build failed: "No space left on device"

The build needs **several GB free**. If it fails:

1. Run `.\clean_build.bat` to remove old `build\`, `dist\`, and `build_temp\` folders.
2. Empty Windows temp: press `Win+R`, type `%TEMP%`, delete old files.
3. Rebuild with `.\build_exe.bat`.

---

## 📄 License

MIT

---

## 📝 Changelog highlights

### v1.7.0 — RapidOCR v5 Quality Upgrade
- Upgraded Persian OCR to **RapidOCR Arabic PP-OCRv5** for better real-world text quality
- Kept **Fast / Accurate** modes and tuned preprocessing behavior for each mode
- Fixed screenshot OCR edge cases (including empty captures) and stabilized progress handling
- Built lightweight standalone `.exe` with bundled ONNX models for offline use

Idea and prototype inspiration for the screen-crop workflow: **[@Meysam-tofiq](https://github.com/Meysam-tofiq)** — thank you!

---

## 🙏 Thanks / تشکر

Special thanks to **[Meysam-tofiq](https://github.com/Meysam-tofiq)** for proposing and prototyping the **screen crop / snip-and-type** idea (`Win+Shift+D`). That contribution helped shape this feature in the main release.

از **[میثم توفیق (@Meysam-tofiq)](https://github.com/Meysam-tofiq)** بابت پیشنهاد و نمونه‌سازی قابلیت **برش صفحه و تایپ زنده** (`Win+Shift+D`) صمیمانه سپاسگزاریم. این ایده در نسخه اصلی پروژه اضافه شد.

OCR is powered by [RapidOCR](https://github.com/RapidAI/RapidOCR). Earlier versions used EasyOCR and Tesseract — thanks to those communities.

موتور OCR فعلی [RapidOCR](https://github.com/RapidAI/RapidOCR) است. نسخه‌های قبلی از EasyOCR و Tesseract استفاده می‌کردند — از جوامع مربوطه سپاسگزاریم.

---

## 🏷️ Keywords | کلیدواژه‌ها

Persian OCR · Farsi OCR · Image to Text · PDF OCR · Screen Snip · Win+Shift+D · RapidOCR · ONNX · Flet · PyMuPDF · OpenCV · Persian Text Recognition · فارسی · تشخیص متن فارسی · OCR فارسی · تبدیل عکس به متن · تبدیل PDF به متن · برش صفحه

---

## 📬 Contact

For questions, suggestions, or collaboration, feel free to reach out:

- 🌐 [Website](https://hamedgh2k04.ir/)
- 💬 [Telegram](https://t.me/Hamedgh_2k04)
- 💼 [LinkedIn](https://www.linkedin.com/in/hamed-gharghi-7b137b364)
- 🐙 [GitHub](https://github.com/Hamed-Gharghi)
- 📧 Email: hamed.gharghi@gmail.com
