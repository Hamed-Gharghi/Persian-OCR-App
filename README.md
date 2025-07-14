
# Persian OCR App 🇮🇷🖼️🔍📝

[![GitHub stars](https://img.shields.io/github/stars/Hamed-Gharghi/Persian-OCR-App?style=social)](https://github.com/Hamed-Gharghi/Persian-OCR-App/stargazers)
[![GitHub issues](https://img.shields.io/github/issues/Hamed-Gharghi/Persian-OCR-App)](https://github.com/Hamed-Gharghi/Persian-OCR-App/issues)
[![GitHub forks](https://img.shields.io/github/forks/Hamed-Gharghi/Persian-OCR-App?style=social)](https://github.com/Hamed-Gharghi/Persian-OCR-App/network/members)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![PySide6](https://img.shields.io/badge/PySide6-Qt%20for%20Python-green?logo=qt)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?logo=windows&logoColor=white)

---

> **Persian OCR App** — Convert Persian (Farsi) images and PDFs to editable text using Tesseract and PySide6. Fast, accurate, and easy-to-use desktop OCR for Persian documents.
> 
> **برنامه OCR فارسی** — تبدیل عکس و PDF فارسی به متن قابل ویرایش با استفاده از Tesseract و PySide6. سریع، دقیق و آسان برای اسناد فارسی.

---

## 📑 Navigation | ناوبری
- [🇬🇧 English](#english)
- [🇮🇷 فارسی](#persian)

---

<a name="english"></a>
# 🇬🇧 English

## 🔑 Key Features & Highlights | نکات کلیدی و ویژگی‌ها
- **Persian (Farsi) OCR | تشخیص متن فارسی**: Extract text from Persian images and PDFs | استخراج متن از عکس و PDF فارسی
- **Easy to Use | استفاده آسان**: Simple drag-and-drop interface | رابط کاربری ساده و کشیدن و رها کردن
- **PDF & Image Support | پشتیبانی از PDF و عکس**: Works with both formats | کار با هر دو فرمت
- **No Internet Needed | بدون نیاز به اینترنت**: All processing is local | تمام پردازش‌ها به صورت محلی
- **Modern GUI | رابط کاربری مدرن**: Built with PySide6 (Qt for Python) | ساخته شده با PySide6
- **Bundled Tesseract | Tesseract همراه**: No separate installation required | بدون نیاز به نصب جداگانه
- **English & Persian UI | رابط کاربری فارسی و انگلیسی**: Switchable interface | قابل تغییر

---

## 🚀 Quick Start
1. **Clone the repository:**
   ```bash
   git clone https://github.com/Hamed-Gharghi/Persian-OCR-App.git
   cd Persian-OCR-App/Persian\ OCR
   ```
2. **Install Python 3.10+** (Recommended: 3.10, 3.11, or 3.12)
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

## ❓ What is Persian OCR? | OCR فارسی چیست؟
Persian OCR (Optical Character Recognition) is the technology to convert scanned Persian (Farsi) documents, images, or PDFs into editable and searchable text. This app makes it easy to extract Persian text from images and PDFs on your computer.

تشخیص نوری حروف (OCR) فارسی، فناوری تبدیل اسناد، تصاویر یا PDF اسکن‌شده فارسی به متن قابل ویرایش و جستجو است. این برنامه استخراج متن فارسی از عکس و PDF را روی کامپیوتر شما آسان می‌کند.

---

<a name="persian"></a>
# 🇮🇷 فارسی

## 🚀 شروع سریع
۱. **کلون کردن مخزن:**
   ```bash
   git clone https://github.com/Hamed-Gharghi/Persian-OCR-App.git
   cd Persian-OCR-App/Persian\ OCR
   ```
۲. **نصب پایتون ۳.۱۰ یا بالاتر (پیشنهادی: ۳.۱۰، ۳.۱۱ یا ۳.۱۲)**
۳. **نصب وابستگی‌ها:**
   ```bash
   pip install -r requirements.txt
   ```
۴. **اجرای برنامه:**
   ```bash
   python main.py
   ```

## ✨ ویژگی‌ها
- 🖥️ رابط کاربری ساده، کاربرپسند و مدرن (حالت تیره/روشن خودکار)
- 🌐 رابط کاربری فارسی و انگلیسی (قابل تغییر)
- 📂 امکان کشیدن و رها کردن یا انتخاب تصویر/PDF
- ⏳ نوار پیشرفت و لاگ لحظه‌ای
- 🖼️ پیش‌نمایش تصویر یا PDF قبل از OCR
- 💾 ذخیره خروجی OCR در فایل متنی
- 📦 بدون نیاز به نصب جداگانه Tesseract (همراه برنامه)

## 📝 نکات
- 📦 برنامه از موتور Tesseract همراه (در پوشه `Tesseract`) برای بیشترین قابلیت حمل استفاده می‌کند.
- 🔒 تمام پردازش‌ها به صورت محلی انجام می‌شود و داده‌ای ارسال نمی‌گردد.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!
Feel free to open an issue or submit a pull request.

---

## ❓ FAQ / Troubleshooting

**Q: Why is the OCR not accurate for some images?**
- A: OCR accuracy depends on image quality, resolution, and clarity. For best results, use high-resolution, well-lit, and straight images. Avoid blurry or skewed scans.

**Q: How do I add more languages?**
- A: Download the desired language data file (traineddata) for Tesseract and place it in the `tessdata` folder. Then select the language in the app settings or code.

**Q: What to do if Tesseract is not detected?**
- A: Make sure the Tesseract executable is included in the app's `Tesseract` folder or installed on your system. Check that the app's settings point to the correct Tesseract path.

---

## 📄 License
MIT

---

## 🙏 Thanks / تشکر
This project uses the amazing [Tesseract OCR engine](https://github.com/tesseract-ocr/tesseract) — thank you to the Tesseract team and contributors!

این پروژه از موتور قدرتمند [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) استفاده می‌کند — از تیم و توسعه‌دهندگان Tesseract سپاسگزاریم!

---

## 🏷️ Keywords | کلیدواژه‌ها

<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">Persian OCR</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">Farsi OCR</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">Image to Text</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">PDF OCR</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">Tesseract</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">PySide6</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">Qt for Python</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">Persian Text Recognition</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">فارسی</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">تشخیص متن فارسی</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">OCR فارسی</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">تبدیل عکس به متن</span>
<span style="display:inline-block;background:#f3f3f3;border-radius:6px;padding:3px 10px;margin:2px 2px;font-size:90%;">تبدیل PDF به متن</span>

---

## 📬 Contact
For questions, suggestions, or collaboration, feel free to reach out:
- 🌐 [Website](https://hamedgh2k04.ir/)
- 💬 [Telegram](https://t.me/Hamedgh_2k04)
- 💼 [LinkedIn](https://www.linkedin.com/in/hamed-gharghi-7b137b364)
- 🐙 [GitHub](https://github.com/Hamed-Gharghi)
- 📧 Email: hamed.gharghi@gmail.com
