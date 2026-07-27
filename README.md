# Persian OCR App 🇮🇷🖼️🔍📝

[![GitHub stars](https://img.shields.io/github/stars/Hamed-Gharghi/Persian-OCR-App?style=social)](https://github.com/Hamed-Gharghi/Persian-OCR-App/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Hamed-Gharghi/Persian-OCR-App)](https://github.com/Hamed-Gharghi/Persian-OCR-App/issues)
[![GitHub forks](https://img.shields.io/github/forks/Hamed-Gharghi/Persian-OCR-App?style=social)](https://github.com/Hamed-Gharghi/Persian-OCR-App/network/members)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
![Version](https://img.shields.io/badge/Version-1.5.0-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Flet](https://img.shields.io/badge/Flet-0.85%2B-purple)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?logo=windows&logoColor=white)

**By [Hamed Gharghi](https://github.com/Hamed-Gharghi)** · [Persian-OCR-App](https://github.com/Hamed-Gharghi/Persian-OCR-App)

---

> **Persian OCR App v1.5** — Convert Persian (Farsi) images and PDFs to editable text using Tesseract OCR and Flet. Includes global screen snip (`Win+Shift+D`) that OCRs a region and types the text into the focused app. Fast, accurate, and easy-to-use desktop OCR for Persian documents.
>
> **برنامه OCR فارسی نسخه ۱.۵** — تبدیل عکس و PDF فارسی به متن قابل ویرایش با استفاده از Tesseract و Flet. دارای برش صفحه سراسری (`Win+Shift+D`) که ناحیه انتخاب‌شده را OCR می‌کند و متن را در برنامه فعال تایپ می‌کند. سریع، دقیق و آسان برای اسناد فارسی.

---

## 🪟 Download for Windows

**No installation or Python required!**

- Download the latest ready-to-use Windows executable (`PersianOCR.exe`) from the [Releases page](https://github.com/Hamed-Gharghi/Persian-OCR-App/releases).
- Just download, double-click, and start using Persian OCR on Windows.
- The `.exe` is fully standalone (~170–190 MB after slim packaging) — Tesseract, language models, and all dependencies are bundled inside.

---

## 🪟 دانلود برای ویندوز

**بدون نیاز به نصب یا پایتون!**

- آخرین نسخه اجرایی ویندوز (`PersianOCR.exe`) را از [صفحه انتشارها](https://github.com/Hamed-Gharghi/Persian-OCR-App/releases) دانلود کنید.
- فقط دانلود کنید، دوبار کلیک کنید و بلافاصله از برنامه OCR فارسی روی ویندوز استفاده کنید.
- فایل اجرایی کاملاً مستقل است (~۱۷۰–۱۹۰ مگابایت با بسته‌بندی بهینه) — Tesseract، مدل‌های زبان و تمام وابستگی‌ها داخل آن قرار دارند.

---

## 📑 Navigation | ناوبری

- [🇬🇧 English](#english)
- [🇮🇷 فارسی](#persian)

---

<a name="english"></a>
# 🇬🇧 English

## 🔑 Key Features

- **Persian (Farsi) OCR** — Extract text from Persian images and PDFs
- **Modern desktop UI** — Built with [Flet](https://flet.dev/) (v0.85+), dark theme, native RTL for Persian
- **Easy to use** — Drag-and-drop (Windows), file picker, or batch folder processing
- **PDF & image support** — PNG, JPG, BMP, and PDF with per-page progress
- **Export formats** — Plain text (`.txt`), Word (`.docx`), and PDF
- **OCR quality modes** — Fast (lighter model) or Accurate (best Persian model)
- **Image enhancement** — Upscale, grayscale, contrast, denoise, deskew, optional binarization
- **Smart layout** — Auto-detect page layout (PSM) or choose manually
- **Persian text cleanup** — Normalizes common OCR character errors (ي→ی, ك→ک, …)
- **Screen snip & type** — Press `Win+Shift+D` (or `Ctrl+Shift+D`) anywhere to crop a screen region, run OCR, and auto-type the text into the focused application
- **Saved settings** — Language, OCR options, and export format persist between sessions
- **Keyboard shortcuts** — `Ctrl+O` open · `Ctrl+C` copy · `Ctrl+S` save · `Win+Shift+D` screen snip
- **Bundled Tesseract 5.5** — No separate installation required
- **Fully offline** — All processing runs locally; no internet needed
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
- 🖼️ پیش‌نمایش تصویر/PDF و پیش‌نمایش تصویر پردازش‌شده قبل از OCR
- ⚙️ بهبود تصویر، باینری‌سازی، تشخیص خودکار چیدمان صفحه
- 🎯 حالت سریع یا دقیق برای مدل فارسی
- ✂️ برش صفحه و تایپ زنده — با `Win+Shift+D` (یا `Ctrl+Shift+D`) بخشی از صفحه را انتخاب کنید؛ متن استخراج و در برنامه فعال تایپ می‌شود
- 💾 خروجی در فرمت txt، docx و pdf
- ⌨️ میانبرهای Ctrl+O / Ctrl+C / Ctrl+S / Win+Shift+D
- 💾 ذخیره تنظیمات بین اجراها
- 📦 Tesseract 5.5 همراه برنامه — بدون نصب جداگانه
- 🔒 پردازش کاملاً محلی — بدون ارسال داده

## 📝 نکات

- 📦 برنامه از موتور Tesseract همراه (در پوشه `Tesseract`) استفاده می‌کند.
- 🔒 تمام پردازش‌ها به صورت محلی انجام می‌شود و داده‌ای ارسال نمی‌گردد.
- 📄 فایل `settings.json` کنار برنامه (یا کنار `.exe`) برای ذخیره تنظیمات ساخته می‌شود.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a pull request.

---

## ❓ FAQ / Troubleshooting

**Q: Why is the OCR not accurate for some images?**

- OCR accuracy depends on image quality, resolution, and clarity. For best results, use high-resolution, well-lit, and straight images. Try **Accurate** mode, enable **Enhance image**, and use **Auto-detect page layout**.

**Q: How do I add more languages?**

- Download the desired Tesseract `traineddata` file and place it in `Tesseract/tessdata/`. Then select the language in the app settings.

**Q: What if Tesseract is not detected?**

- Make sure the `Tesseract` folder (with `tesseract.exe` and `tessdata/`) is next to `main.py` when running from source, or bundled inside `PersianOCR.exe` when using the release build.

**Q: PDF OCR fails with a Poppler error?**

- Older builds used `pdf2image`, which required Poppler. **v1.5+** uses **PyMuPDF** — no Poppler install is needed. Rebuild with `build_exe.bat` if you still see this error.

**Q: Does drag-and-drop work on Linux or macOS?**

- Drag-and-drop onto the window is supported on **Windows** only (`windnd`). On other platforms, use the file picker or **Process Folder**.

---

## 🛠️ Build a single Windows `.exe`

The release build bundles Python, Flet, PyMuPDF, OpenCV, Tesseract, and tessdata into one file. Poppler is **not** needed.

1. Ensure the full `Tesseract` folder is in the project root (`tesseract.exe`, `tessdata/`, `model_store/`).
2. **Optional:** Delete `Tesseract/tesseract-ocr-w64-setup-*.exe` if present (the Windows installer is not needed and can add tens of MB to the build).
3. Test from source:

   ```bat
   pip install -r requirements.txt
   python main.py
   ```

4. Build the executable:

   **Command Prompt or PowerShell** (note the `.\` prefix in PowerShell):

   ```bat
   .\build_exe.bat
   ```

   Or from PowerShell:

   ```powershell
   .\build_exe.ps1
   ```

   `build_exe.bat` runs `prepare_release.py` first to strip training tools, docs, duplicate backups, and unused language packs before packing. Temp files are stored in `build_temp\` on the project drive (not `C:\Users\...\Temp`) to avoid filling system drive C:.

5. Output: `dist\PersianOCR.exe` — share this single file; users do not need Python or Tesseract installed.

### Smaller exe (lite build)

For an even smaller release (~10 MB less), use the lighter English model:

```powershell
.\build_exe.ps1 -Lite
```

Or in Command Prompt:

```bat
set LITE=1
.\build_exe.bat
```

Accurate Persian OCR is unchanged; English recognition in mixed documents may be slightly less accurate.

### Build failed: "No space left on device"

The build needs **~2 GB free** temporarily. If it fails:

1. Run `.\clean_build.bat` to remove old `build\`, `dist\`, and `build_temp\` folders.
2. Empty Windows temp: press `Win+R`, type `%TEMP%`, delete old files.
3. Rebuild with `.\build_exe.ps1` or `.\build_exe.bat`.

### Why is the exe still large?

Most of the size comes from **OpenCV**, **PyMuPDF**, **Flet**, and **Tesseract DLLs** (required at runtime). The slim bundle removes training tools, docs, duplicate backups, and extra language packs. Going much smaller would mean dropping features (e.g. image enhancement or bilingual models).

---

## 📄 License

MIT

---

## 📝 Changelog highlights

### v1.5 — Screen Snip & Type
- Global hotkey screen crop (`Win+Shift+D` / `Ctrl+Shift+D`): OCR a selected region and type the result into the focused app
- Windowed standalone `.exe` build (no console flash)

Idea and prototype inspiration for the screen-crop workflow: **[@Meysam-tofiq](https://github.com/Meysam-tofiq)** — thank you!

---

## 🙏 Thanks / تشکر

Special thanks to **[Meysam-tofiq](https://github.com/Meysam-tofiq)** for proposing and prototyping the **screen crop / snip-and-type** idea (`Win+Shift+D`). That contribution helped shape this feature in the main release.

از **[میثم توفیق (@Meysam-tofiq)](https://github.com/Meysam-tofiq)** بابت پیشنهاد و نمونه‌سازی قابلیت **برش صفحه و تایپ زنده** (`Win+Shift+D`) صمیمانه سپاسگزاریم. این ایده در نسخه اصلی پروژه اضافه شد.

This project also uses the amazing [Tesseract OCR engine](https://github.com/tesseract-ocr/tesseract) — thank you to the Tesseract team and contributors!

این پروژه از موتور قدرتمند [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) نیز استفاده می‌کند — از تیم و توسعه‌دهندگان Tesseract سپاسگزاریم!

---

## 🏷️ Keywords | کلیدواژه‌ها

Persian OCR · Farsi OCR · Image to Text · PDF OCR · Screen Snip · Win+Shift+D · Tesseract · Flet · PyMuPDF · OpenCV · Persian Text Recognition · فارسی · تشخیص متن فارسی · OCR فارسی · تبدیل عکس به متن · تبدیل PDF به متن · برش صفحه

---

## 📬 Contact

For questions, suggestions, or collaboration, feel free to reach out:

- 🌐 [Website](https://hamedgh2k04.ir/)
- 💬 [Telegram](https://t.me/Hamedgh_2k04)
- 💼 [LinkedIn](https://www.linkedin.com/in/hamed-gharghi-7b137b364)
- 🐙 [GitHub](https://github.com/Hamed-Gharghi)
- 📧 Email: hamed.gharghi@gmail.com
