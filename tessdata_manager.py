import os
import shutil
import sys


def _resource_dir():
    if getattr(sys, "frozen", False):
        for base in (getattr(sys, "_MEIPASS", ""), os.path.dirname(sys.executable)):
            if base and os.path.isdir(os.path.join(base, "Tesseract")):
                return base
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _paths():
    base = os.path.join(_resource_dir(), "Tesseract")
    tessdata = os.path.join(base, "tessdata")
    store = os.path.join(base, "model_store")
    backup = os.path.join(base, "backup_fast_models")
    return {
        "tessdata": tessdata,
        "store": store,
        "active_fas": os.path.join(tessdata, "fas.traineddata"),
        "best_fas": os.path.join(store, "fas_best.traineddata"),
        "fast_fas": os.path.join(store, "fas_fast.traineddata"),
        "backup_fast_fas": os.path.join(backup, "fas.traineddata"),
    }


def ensure_model_store():
    paths = _paths()
    os.makedirs(paths["store"], exist_ok=True)

    if not os.path.isfile(paths["best_fas"]) and os.path.isfile(paths["active_fas"]):
        shutil.copy2(paths["active_fas"], paths["best_fas"])

    if not os.path.isfile(paths["fast_fas"]):
        if os.path.isfile(paths["backup_fast_fas"]):
            shutil.copy2(paths["backup_fast_fas"], paths["fast_fas"])
        elif os.path.isfile(paths["active_fas"]):
            shutil.copy2(paths["active_fas"], paths["fast_fas"])


def apply_ocr_mode(mode):
    ensure_model_store()
    paths = _paths()
    source = paths["fast_fas"] if mode == "fast" else paths["best_fas"]
    if os.path.isfile(source):
        shutil.copy2(source, paths["active_fas"])


def trim_unused_tessdata():
    tessdata = _paths()["tessdata"]
    for name in (
        "enm.traineddata",
        "osd.traineddata",
        "jaxb-api-2.3.1.jar",
        "piccolo2d-core-3.0.1.jar",
        "piccolo2d-extras-3.0.1.jar",
        "ScrollView.jar",
        "pdf.ttf",
    ):
        path = os.path.join(tessdata, name)
        if os.path.isfile(path):
            os.remove(path)
