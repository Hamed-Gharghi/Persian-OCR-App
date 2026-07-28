"""RapidOCR (ONNX Runtime) Persian/English OCR helpers — lightweight, no PyTorch."""

import os
import re
import sys
import threading
import unicodedata

import numpy as np
from PIL import Image, ImageEnhance

_engines = {}
_engine_lock = threading.Lock()
_infer_lock = threading.Lock()


class OCRCancelled(Exception):
    """Raised when the user cancels OCR mid-run."""


_MIN_CONF = 0.55
_LINE_Y_TOL = 0.55
_OVERLAP_MERGE = 0.22
_TARGET_LONG_SIDE_FAST = 1280
_TARGET_LONG_SIDE_ACCURATE = 1600
_MAX_LONG_SIDE = 1800
_ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

_OCR_FIXES = [
    (re.compile(r"قدر\s*ز?تمند"), "قدرتمند"),
    (re.compile(r"قدر\s+تمند"), "قدرتمند"),
    (re.compile(r"تغییر\s+ات"), "تغییرات"),
    (re.compile(r"تغييرات"), "تغییرات"),
    (re.compile(r"جادويى"), "جادویی"),
    (re.compile(r"تصو\s*یر"), "تصویر"),
    (re.compile(r"تصويرسازى"), "تصویرسازی"),
    (re.compile(r"تصویرایی"), "تصویرسازی"),
    (re.compile(r"خودهی[نپ]وتیزمی"), "خودهیپنوتیزمی"),
    (re.compile(r"خودهینوتیزمی"), "خودهیپنوتیزمی"),
    (re.compile(r"(?<!خود)(?<!خودهی)هیپنوتیزمی\b"), "هیپنوتیزم"),
    (re.compile(r"عصابی"), "عصبی"),
    (re.compile(r"سهیا"), "مهیا"),
    (re.compile(r"کذشته"), "گذشته"),
    (re.compile(r"گنشته"), "گذشته"),
    (re.compile(r"تلهها"), "تله ها"),
    (re.compile(r"تله هاو"), "تله ها و"),
    (re.compile(r"کهبه"), "که به"),
    (re.compile(r"کهشما"), "که شما"),
    (re.compile(r"شماکمک"), "شما کمک"),
    (re.compile(r"خودرا"), "خود را"),
    (re.compile(r"ایدکه"), "اید که"),
    (re.compile(r"اید\؟?\s*راهی"), "اید؟ راهی"),
    (re.compile(r"ایداراهی"), "اید؟ راهی"),
    (re.compile(r"آیا\s*تا"), "آیا تا"),
    (re.compile(r"آیاتا"), "آیا تا"),
    (re.compile(r"بایان"), "پایان"),
    (re.compile(r"بايان"), "پایان"),
    (re.compile(r"رابه\b"), "را به"),
    (re.compile(r"وشروع"), "و شروع"),
    (re.compile(r"وبه\b"), "و به"),
    (re.compile(r"تابه\b"), "تا به"),
    (re.compile(r"(?<!\w)ایا(?!\w)"), "آیا"),
    (re.compile(r"درکدام"), "در کدام"),
    (re.compile(r"بهشما"), "به شما"),
    (re.compile(r"ازگذشته"), "از گذشته"),
    (re.compile(r"دران\b"), "در آن"),
    (re.compile(r"عمیق\s*ترکه"), "عمیق‌تر که"),
    (re.compile(r"\s*-\s*\d+\s*$", re.M), ""),
    (re.compile(r"[‐‑‒–—―]\s*\d+"), ""),
]


def _parse_lang(lang):
    raw = (lang or "fas+eng").strip().lower().replace(" ", "")
    if raw in ("eng", "en", "english"):
        return {"key": "en", "rtl": False, "persian_norm": False}
    if raw in ("fas", "fa", "persian", "farsi", "fas+eng", "fa+en", "fa+eng"):
        # Arabic-script mobile model covers Persian; mixed docs still use it
        return {"key": "fa", "rtl": True, "persian_norm": True}
    return {"key": "fa", "rtl": True, "persian_norm": True}


def _resolve_model_dir():
    candidates = []
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "rapidocr_models"))
        candidates.append(os.path.join(os.path.dirname(sys.executable), "rapidocr_models"))
    else:
        candidates.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "rapidocr_models"))
    for path in candidates:
        if os.path.isdir(path) and os.listdir(path):
            return os.path.abspath(path)
    return None


def _create_engine(lang_key):
    from rapidocr import EngineType, LangRec, ModelType, OCRVersion, RapidOCR

    if lang_key == "en":
        rec_lang = LangRec.EN
        rec_version = OCRVersion.PPOCRV4
        rec_name = "en_PP-OCRv4_rec_mobile.onnx"
    else:
        # PP-OCRv5 Arabic is dramatically better for Persian than v4,
        # and already returns logical (not visually reversed) text.
        rec_lang = LangRec.ARABIC
        rec_version = OCRVersion.PPOCRV5
        rec_name = "arabic_PP-OCRv5_rec_mobile.onnx"

    params = {
        "Det.engine_type": EngineType.ONNXRUNTIME,
        "Cls.engine_type": EngineType.ONNXRUNTIME,
        "Rec.engine_type": EngineType.ONNXRUNTIME,
        "Rec.lang_type": rec_lang,
        "Rec.model_type": ModelType.MOBILE,
        "Rec.ocr_version": rec_version,
        "Global.text_score": 0.5,
    }

    model_dir = _resolve_model_dir()
    if model_dir:
        params["Global.model_root_dir"] = model_dir
        det = os.path.join(model_dir, "PP-OCRv6_det_small.onnx")
        cls = os.path.join(model_dir, "ch_ppocr_mobile_v2.0_cls_mobile.onnx")
        rec = os.path.join(model_dir, rec_name)
        if os.path.isfile(det):
            params["Det.model_path"] = det
        if os.path.isfile(cls):
            params["Cls.model_path"] = cls
        if os.path.isfile(rec):
            params["Rec.model_path"] = rec

    print(f"[rapidocr] Initializing lang={lang_key} ({rec_lang} {rec_version})...")
    engine = RapidOCR(params=params)
    print("[rapidocr] Ready.")
    return engine


def get_engine(lang_key="fa"):
    cached = _engines.get(lang_key)
    if cached is not None:
        return cached
    with _engine_lock:
        cached = _engines.get(lang_key)
        if cached is not None:
            return cached
        engine = _create_engine(lang_key)
        _engines[lang_key] = engine
        return engine


def warm_reader():
    """Load default Persian/Arabic RapidOCR models in the background."""
    get_engine("fa")


def normalize_persian_text(text):
    if not text:
        return text

    text = unicodedata.normalize("NFC", text)
    replacements = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "أ": "ا",
        "إ": "ا",
        "ؤ": "و",
        "ة": "ه",
        "ۀ": "ه",
        "\u0640": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)

    for pattern, repl in _OCR_FIXES:
        text = pattern.sub(repl, text)

    while "  " in text:
        text = text.replace("  ", " ")
    lines = []
    for line in text.splitlines():
        stripped = line.strip(" -\t")
        if not stripped:
            continue
        if len(stripped) <= 2 and stripped.isdigit():
            continue
        lines.append(line.rstrip())
    return "\n".join(lines).strip()


def _box_metrics(bbox):
    xs = [float(p[0]) for p in bbox]
    ys = [float(p[1]) for p in bbox]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    return {
        "left": left,
        "right": right,
        "top": top,
        "bottom": bottom,
        "cy": (top + bottom) / 2.0,
        "height": max(bottom - top, 1.0),
        "width": max(right - left, 1.0),
    }


def _cluster_lines(items):
    if not items:
        return []
    items = sorted(items, key=lambda it: it["cy"])
    lines = [[items[0]]]
    for item in items[1:]:
        line = lines[-1]
        avg_cy = sum(i["cy"] for i in line) / len(line)
        avg_h = sum(i["height"] for i in line) / len(line)
        if abs(item["cy"] - avg_cy) <= avg_h * _LINE_Y_TOL:
            line.append(item)
        else:
            lines.append([item])
    return lines


def _join_line(line_items, rtl=True):
    if not line_items:
        return ""
    if rtl:
        ordered = sorted(line_items, key=lambda it: it["right"], reverse=True)
    else:
        ordered = sorted(line_items, key=lambda it: it["left"])

    cleaned = []
    for it in ordered:
        piece = " ".join((it["text"] or "").split())
        if piece:
            cleaned.append({**it, "text": piece})
    if not cleaned:
        return ""

    parts = [cleaned[0]["text"]]
    for prev, curr in zip(cleaned, cleaned[1:]):
        overlap = min(prev["right"], curr["right"]) - max(prev["left"], curr["left"])
        min_w = min(prev["width"], curr["width"])
        if min_w > 0 and overlap / min_w >= _OVERLAP_MERGE:
            parts.append(curr["text"])
        else:
            parts.append(" " + curr["text"])
    return "".join(parts)


def _assemble_text(items, rtl=True):
    # RapidOCR returns one text per detection box (line). Keep reading order top→bottom.
    if not items:
        return ""
    # Word-box fallback: many short fragments on similar Y → cluster into lines.
    avg_len = sum(len((it.get("text") or "").strip()) for it in items) / max(len(items), 1)
    if avg_len < 6 and len(items) > 3:
        lines = _cluster_lines(items)
        lines.sort(key=lambda line: sum(i["top"] for i in line) / len(line))
        return "\n".join(_join_line(line, rtl=rtl) for line in lines if line)
    ordered = sorted(items, key=lambda it: (it["top"], -it["right"] if rtl else it["left"]))
    return "\n".join((it["text"] or "").strip() for it in ordered if (it.get("text") or "").strip())


def _looks_like_noise(text, conf):
    """Drop garbage lines (dots/spaces/latin noise) that Arabic v5 sometimes emits."""
    compact = re.sub(r"\s+", "", text)
    if not compact:
        return True
    arabic = len(_ARABIC_RE.findall(compact))
    if arabic == 0:
        return True
    if len(compact) <= 2 and conf < 0.85:
        return True
    if arabic / max(len(compact), 1) < 0.45 and conf < 0.75:
        return True
    # Mostly isolated short glyphs / tatweel noise
    if arabic <= 3 and len(compact) <= 6 and conf < 0.7:
        return True
    return False


def _items_from_rapid(result, rtl=True):
    """Convert RapidOCR output into box items for line assembly.

    PP-OCRv5 Arabic already returns logical Persian text — do NOT reverse it.
    (v4 emitted visual order; reversing was needed there and breaks v5.)
    """
    items = []
    if result is None:
        return items

    boxes = getattr(result, "boxes", None)
    txts = getattr(result, "txts", None)
    scores = getattr(result, "scores", None)
    if boxes is None:
        boxes = []
    if txts is None:
        txts = []
    if scores is None:
        scores = []

    for i, text in enumerate(txts):
        text = (text or "").strip()
        if not text:
            continue
        conf = float(scores[i]) if i < len(scores) else 1.0
        if conf < _MIN_CONF:
            continue
        if rtl and _looks_like_noise(text, conf):
            continue
        if i < len(boxes):
            m = _box_metrics(boxes[i])
        else:
            m = {
                "left": 0,
                "right": 1,
                "top": float(i),
                "bottom": float(i) + 1,
                "cy": float(i),
                "height": 1.0,
                "width": 1.0,
            }
        m["text"] = text
        m["conf"] = conf
        items.append(m)
    if items:
        return items

    # Rare fallback: word boxes. Shape varies — lines of tuples, or a flat tuple list.
    word_results = getattr(result, "word_results", None)
    if not word_results:
        return items

    def _consume_entry(entry):
        if not entry or not isinstance(entry, (tuple, list)) or len(entry) < 3:
            return
        text, conf, box = entry[0], float(entry[1]), entry[2]
        text = (text or "").strip()
        if not text or box is None or conf < _MIN_CONF:
            return
        m = _box_metrics(box)
        m["text"] = text
        m["conf"] = conf
        items.append(m)

    first = word_results[0]
    if isinstance(first, (tuple, list)) and len(first) >= 3 and not isinstance(first[0], (tuple, list)):
        # Flat: ((text, score, box), ...)
        for entry in word_results:
            _consume_entry(entry)
    else:
        # Nested: [ [(text, score, box), ...], ... ]
        for line in word_results:
            if not line:
                continue
            if isinstance(line, (tuple, list)) and len(line) >= 3 and isinstance(line[0], str):
                _consume_entry(line)
                continue
            for entry in line:
                _consume_entry(entry)
    return items


def _prepare_base(image, mode):
    """Mode-aware preprocess for RapidOCR.

    fast: smaller working size (quicker)
    accurate: keep detail / upscale small snips more aggressively
    """
    image = image.convert("RGB")
    w, h = image.size
    long_side = max(w, h)
    if long_side <= 0:
        return image

    if mode in ("fast", "speed", "quick"):
        image = ImageEnhance.Contrast(image).enhance(1.05)
        target = _TARGET_LONG_SIDE_FAST
        # Downscale large pages for speed; light upscale only for tiny snips
        if long_side > target:
            scale = target / long_side
        elif long_side < 640:
            scale = min(960 / long_side, _MAX_LONG_SIDE / long_side)
        else:
            return image
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        return image.resize((nw, nh), Image.Resampling.BILINEAR)

    # accurate
    image = ImageEnhance.Contrast(image).enhance(1.12)
    target = _TARGET_LONG_SIDE_ACCURATE
    if long_side < 1100:
        scale = min(target / long_side, _MAX_LONG_SIDE / long_side)
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        return image.resize((nw, nh), Image.Resampling.LANCZOS)
    return image


def _cancelled(cancel_check):
    try:
        return bool(cancel_check and cancel_check())
    except Exception:
        return False


def _run_engine(engine, img_np, cancel_check, return_word_box=False):
    if _cancelled(cancel_check):
        raise OCRCancelled()
    box = {"result": None, "error": None}
    done = threading.Event()

    def worker():
        try:
            with _infer_lock:
                if _cancelled(cancel_check):
                    return
                box["result"] = engine(img_np, return_word_box=return_word_box)
        except Exception as exc:
            box["error"] = exc
        finally:
            done.set()

    threading.Thread(target=worker, daemon=True).start()
    while not done.wait(0.12):
        if _cancelled(cancel_check):
            raise OCRCancelled()
    if _cancelled(cancel_check):
        raise OCRCancelled()
    if box["error"] is not None:
        raise box["error"]
    return box["result"]


def run_ocr(image, lang="fas+eng", mode="accurate", progress_cb=None, cancel_check=None, **_ignored):
    """Run RapidOCR on a PIL image and return plain text."""

    def report(fraction, stage=""):
        if progress_cb:
            try:
                progress_cb(max(0.0, min(1.0, float(fraction))), stage)
            except Exception:
                pass

    def checkpoint():
        if _cancelled(cancel_check):
            raise OCRCancelled()

    lang_cfg = _parse_lang(lang)
    mode = (mode or "accurate").strip().lower()

    checkpoint()
    report(0.05, "prepare")
    engine = get_engine(lang_cfg["key"])
    checkpoint()
    report(0.12, "prepare")
    base = _prepare_base(image, mode)
    img_np = np.array(base)

    checkpoint()
    report(0.2, "pass 1/1")
    result = _run_engine(engine, img_np, cancel_check, return_word_box=False)
    report(0.85, "pass 1/1")

    checkpoint()
    report(0.92, "merge")
    if result is None:
        report(1.0, "done")
        return ""

    items = _items_from_rapid(result, rtl=lang_cfg["rtl"])
    text = _assemble_text(items, rtl=lang_cfg["rtl"])

    if lang_cfg["persian_norm"]:
        text = normalize_persian_text(text)
    else:
        while "  " in text:
            text = text.replace("  ", " ")
        text = text.strip()

    report(1.0, "done")
    return text


def run_ocr_fast(image, lang="fas+eng", **kwargs):
    kwargs.pop("mode", None)
    return run_ocr(image, lang=lang, mode="fast", **kwargs)
