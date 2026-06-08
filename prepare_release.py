"""Build a slim data bundle for PersianOCR.exe (smaller than full Tesseract/)."""

import argparse
import os
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SRC = os.path.join(ROOT, "Tesseract")
DEFAULT_DST = os.path.join(ROOT, "build_data", "Tesseract")
ASSETS_DST = os.path.join(ROOT, "build_data", "assets")

RUNTIME_EXES = {"tesseract.exe"}
SKIP_DIRS = {"doc", "backup_fast_models", "tessconfigs"}
ENG_FAST_URL = (
    "https://github.com/tesseract-ocr/tessdata_fast/raw/main/eng.traineddata"
)


def folder_size(path):
    total = 0
    for base, _, files in os.walk(path):
        for name in files:
            total += os.path.getsize(os.path.join(base, name))
    return total


def should_skip_file(name):
    if name.endswith(".html"):
        return True
    if name.endswith(".exe"):
        return name not in RUNTIME_EXES
    if name.startswith("tesseract-ocr-w64-setup"):
        return True
    if name in {"tesseract-uninstall.exe", "winpath.exe"}:
        return True
    return False


def resolve_fas_seed(src):
    """Ship the small fast model in tessdata/; accurate mode swaps from model_store."""
    candidates = [
        os.path.join(src, "model_store", "fas_fast.traineddata"),
        os.path.join(src, "backup_fast_models", "fas.traineddata"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return os.path.join(src, "tessdata", "fas.traineddata")


def resolve_eng_model(src, lite):
    if lite:
        local = os.path.join(src, "tessdata_fast", "eng.traineddata")
        if os.path.isfile(local):
            return local, "local tessdata_fast"
        cache = os.path.join(ROOT, "build_data", "cache", "eng_fast.traineddata")
        if os.path.isfile(cache):
            return cache, "cached tessdata_fast"
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        print(f"Downloading smaller English model (~4 MB)...")
        urllib.request.urlretrieve(ENG_FAST_URL, cache)
        return cache, "downloaded tessdata_fast"
    return os.path.join(src, "tessdata", "eng.traineddata"), "tessdata_best"


def prepare_tesseract(src, dst, lite=False):
    if not os.path.isdir(src):
        print(f"ERROR: Tesseract folder not found: {src}", file=sys.stderr)
        sys.exit(1)

    if os.path.isdir(dst):
        shutil.rmtree(dst)
    os.makedirs(dst, exist_ok=True)

    for name in os.listdir(src):
        src_path = os.path.join(src, name)
        if os.path.isdir(src_path):
            continue
        if should_skip_file(name):
            continue
        shutil.copy2(src_path, os.path.join(dst, name))

    tess_src = os.path.join(src, "tessdata")
    tess_dst = os.path.join(dst, "tessdata")
    os.makedirs(tess_dst, exist_ok=True)

    fas_seed = resolve_fas_seed(src)
    if os.path.isfile(fas_seed):
        shutil.copy2(fas_seed, os.path.join(tess_dst, "fas.traineddata"))

    eng_src, eng_label = resolve_eng_model(src, lite)
    if os.path.isfile(eng_src):
        shutil.copy2(eng_src, os.path.join(tess_dst, "eng.traineddata"))
        print(f"English model: {eng_label}")
    else:
        print(f"ERROR: English model not found: {eng_src}", file=sys.stderr)
        sys.exit(1)

    configs_src = os.path.join(tess_src, "configs")
    if os.path.isdir(configs_src):
        shutil.copytree(configs_src, os.path.join(tess_dst, "configs"))

    store_src = os.path.join(src, "model_store")
    if os.path.isdir(store_src):
        shutil.copytree(store_src, os.path.join(dst, "model_store"))

    required = [
        os.path.join(dst, "tesseract.exe"),
        os.path.join(tess_dst, "fas.traineddata"),
        os.path.join(tess_dst, "eng.traineddata"),
    ]
    missing = [p for p in required if not os.path.isfile(p)]
    if missing:
        print("ERROR: Slim bundle is missing required files:", file=sys.stderr)
        for path in missing:
            print(f"  - {path}", file=sys.stderr)
        sys.exit(1)


def prepare_assets():
    icon_src = os.path.join(ROOT, "assets", "icon.ico")
    if not os.path.isfile(icon_src):
        print(f"ERROR: Icon not found: {icon_src}", file=sys.stderr)
        sys.exit(1)
    if os.path.isdir(ASSETS_DST):
        shutil.rmtree(ASSETS_DST)
    os.makedirs(ASSETS_DST, exist_ok=True)
    shutil.copy2(icon_src, os.path.join(ASSETS_DST, "icon.ico"))


def main():
    parser = argparse.ArgumentParser(description="Prepare slim release bundle for exe build")
    parser.add_argument("--src", default=DEFAULT_SRC, help="Source Tesseract folder")
    parser.add_argument("--dst", default=DEFAULT_DST, help="Output slim Tesseract folder")
    parser.add_argument(
        "--lite",
        action="store_true",
        help="Use smaller English model (tessdata_fast, ~10 MB smaller)",
    )
    args = parser.parse_args()

    src_mb = folder_size(args.src) / (1024 * 1024)
    prepare_tesseract(args.src, args.dst, lite=args.lite)
    prepare_assets()
    dst_mb = folder_size(args.dst) / (1024 * 1024)
    assets_mb = folder_size(ASSETS_DST) / (1024 * 1024)

    print(f"Tesseract source: {src_mb:.1f} MB")
    print(f"Slim Tesseract:   {dst_mb:.1f} MB  (saved ~{max(0, src_mb - dst_mb):.1f} MB)")
    print(f"Assets bundle:    {assets_mb:.1f} MB")
    print(f"Ready: {args.dst}")


if __name__ == "__main__":
    main()
