import unicodedata

import cv2
import numpy as np
from PIL import Image

MIN_OCR_WIDTH = 1500

PSM_REASONS = {
    "single_line": {"en": "single line of text", "fa": "یک خط متن"},
    "sparse": {"en": "sparse text", "fa": "متن پراکنده"},
    "screenshot": {"en": "screenshot / UI", "fa": "اسکرین‌شات / رابط کاربری"},
    "document": {"en": "full document", "fa": "سند کامل"},
}


def build_tesseract_config(psm=3, oem=1):
    return f'--psm {psm} --oem {oem}'


def upscale_if_needed(image, min_width=MIN_OCR_WIDTH):
    width, height = image.size
    if width >= min_width:
        return image
    scale = min_width / width
    new_size = (min_width, max(1, int(height * scale)))
    return image.resize(new_size, Image.Resampling.LANCZOS)


def preprocess_image(image, binarize=False, upscale=True):
    image = image.convert("RGB")
    if upscale:
        image = upscale_if_needed(image)

    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    gray = cv2.fastNlMeansDenoising(gray, h=10)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    gray = _deskew(gray)

    if binarize:
        gray = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 15
        )

    return Image.fromarray(gray)


def suggest_psm(image):
    img = np.array(image.convert("RGB"))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    height, width = gray.shape
    aspect = width / max(height, 1)

    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    text_ratio = float(np.count_nonzero(binary)) / binary.size
    color_std = float(np.std(img.reshape(-1, 3), axis=0).mean())

    num_labels, _, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    significant = sum(
        1 for i in range(1, num_labels) if stats[i, cv2.CC_STAT_AREA] > 50
    )

    if height < 80 and aspect > 4:
        return 7, "single_line"
    if text_ratio < 0.05 and significant < 30:
        return 11, "sparse"
    if color_std > 35 and text_ratio > 0.08:
        return 6, "screenshot"
    return 3, "document"


def get_psm_reason_label(reason, language="fa"):
    labels = PSM_REASONS.get(reason, PSM_REASONS["document"])
    return labels.get(language, labels["en"])


def normalize_persian_text(text):
    if not text:
        return text

    text = unicodedata.normalize("NFC", text)
    replacements = {
        "ي": "ی",
        "ك": "ک",
        "ة": "ه",
        "ۀ": "ه",
        "\u0640": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def _deskew(gray):
    inverted = cv2.bitwise_not(gray)
    coords = np.column_stack(np.where(inverted > 0))
    if len(coords) < 100:
        return gray

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = 90 + angle
    elif angle > 45:
        angle = angle - 90

    if abs(angle) < 0.5:
        return gray

    height, width = gray.shape
    center = (width // 2, height // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        gray, matrix, (width, height),
        flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE,
    )


def run_ocr(
    image,
    tesseract_path,
    lang="fas+eng",
    tesseract_config=None,
    preprocess=True,
    binarize=False,
    auto_psm=False,
    psm=None,
):
    import os
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    os.environ["TESSDATA_PREFIX"] = os.path.join(os.path.dirname(tesseract_path), "tessdata")

    working_image = image.convert("RGB")
    if preprocess:
        working_image = preprocess_image(working_image, binarize=binarize, upscale=True)
    else:
        working_image = upscale_if_needed(working_image)

    if auto_psm:
        psm, _ = suggest_psm(image)
        config = build_tesseract_config(psm=psm)
    else:
        config = tesseract_config or build_tesseract_config(psm=psm or 3)
    text = pytesseract.image_to_string(working_image, lang=lang, config=config)

    if "fas" in lang:
        text = normalize_persian_text(text)
    return text


def run_ocr_fast(image, tesseract_path, lang="fas+eng"):
    """
    Speed-optimized OCR for the snipping tool workflow.

    Skips upscaling (screenshots are already high-res), uses PSM 6 (single
    uniform block), and applies only minimal preprocessing for low latency.
    """
    import os
    import pytesseract

    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    os.environ["TESSDATA_PREFIX"] = os.path.join(os.path.dirname(tesseract_path), "tessdata")

    # Minimal preprocessing — no upscaling (screen capture is already crisp)
    working_image = image.convert("RGB")
    img = cv2.cvtColor(np.array(working_image), cv2.COLOR_RGB2GRAY)
    # Light CLAHE for contrast, skip heavy denoising
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    img = clahe.apply(img)
    processed = Image.fromarray(img)

    # PSM 6 = single uniform block of text (ideal for UI captures)
    config = build_tesseract_config(psm=6, oem=1)
    text = pytesseract.image_to_string(processed, lang=lang, config=config)

    if "fas" in lang:
        text = normalize_persian_text(text)
    return text.strip()
