"""
Snipping to Live Typing module for Persian OCR App.

Provides a globally accessible screen-snipping overlay triggered via
Win + Shift + D that captures a screen region, runs fast OCR, and
auto-types the extracted Persian text into the focused application.

Uses tkinter for the overlay (built-in, no extra dependency),
mss for fast screen capture, and pyautogui for text injection.
"""

import threading
import time
import tkinter as tk
from threading import Lock
from typing import Callable

import mss
from PIL import Image
from pynput import keyboard

# ── Module-level configuration (set once from main.py) ──────────────────────

_tesseract_path: str | None = None
_lang: str = "fas+eng"
_fast_mode: bool = True
_on_start: Callable | None = None
_on_end: Callable | None = None
_on_text_extracted: Callable[[str, str], None] | None = None
_lock: Lock = Lock()
_snipping_active: bool = False


def configure(
    *,
    tesseract_path: str,
    lang: str = "fas+eng",
    fast_mode: bool = True,
    on_start: Callable | None = None,
    on_end: Callable | None = None,
    on_text_extracted: Callable[[str, str], None] | None = None,
) -> None:
    """Pass OCR settings from the main app to the snipping tool.

    Args:
        tesseract_path: Path to the Tesseract executable.
        lang: OCR language string (default "fas+eng").
        fast_mode: Whether to use fast OCR mode.
        on_start: Optional callback invoked just before the snipping overlay
                  appears (e.g. to minimise the main window).
        on_end: Optional callback invoked after snipping completes or is
                cancelled (e.g. to restore the main window).
        on_text_extracted: Optional callback invoked after OCR extracts text                           from the snipped region, receiving the text string and
                           the chosen language code."""
    global _tesseract_path, _lang, _fast_mode, _on_start, _on_end, _on_text_extracted
    _tesseract_path = tesseract_path
    _lang = lang
    _fast_mode = fast_mode
    if on_start is not None:
        _on_start = on_start
    if on_end is not None:
        _on_end = on_end
    if on_text_extracted is not None:
        _on_text_extracted = on_text_extracted


# ── Hotkey listener ────────────────────────────────────────────────────────

def _on_hotkey() -> None:
    """Callback invoked when the global hotkey is pressed."""
    print("[snipping] Hotkey triggered!")
    global _snipping_active
    with _lock:
        if _snipping_active:
            return
        _snipping_active = True

    try:
        if _on_start:
            _on_start()
        _run_snipping_workflow()
    finally:
        if _on_end:
            _on_end()
        with _lock:
            _snipping_active = False


def start_hotkey_listener() -> None:
    """Register global hotkeys on a daemon background thread.

    Listens for both Win+Shift+D and Ctrl+Shift+D (the latter as a fallback
    in case Windows intercepts the Win key).
    """
    print("[snipping] Starting global hotkey listener...")

    def _listen():
        try:
            with keyboard.GlobalHotKeys(
                {
                    "<cmd>+<shift>+d": _on_hotkey,
                    "<ctrl>+<shift>+d": _on_hotkey,
                }
            ) as listener:
                listener.join()
        except Exception as exc:
            print(f"[snipping] Failed to register global hotkey: {exc}")

    thread = threading.Thread(target=_listen, daemon=True)
    thread.start()


# ── Snipping overlay (tkinter) ─────────────────────────────────────────────

class _SnippingOverlay:
    """Full-screen, borderless, semi-transparent overlay for region selection.

    Displays a dimmed full-screen window with a crosshair cursor.  The user
    clicks and drags to draw a blue selection rectangle.  On mouse release the
    chosen screen coordinates are returned.
    """

    def __init__(self):
        import ctypes

        # ── DPI awareness (Windows) ────────────────────────────────────────
        # Force per-monitor DPI awareness so tkinter coordinates match mss
        # screen coordinates even when display scaling is > 100%.
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # ── Virtual-screen geometry (multi-monitor) ────────────────────────
        # Calculate the bounding box that covers ALL connected monitors so the
        # dim overlay and coordinate system span every display.
        _virtual_ok = False
        try:
            user32 = ctypes.windll.user32
            SM_XVIRTUALSCREEN = 76
            SM_YVIRTUALSCREEN = 77
            SM_CXVIRTUALSCREEN = 78
            SM_CYVIRTUALSCREEN = 79
            _v_left = user32.GetSystemMetrics(SM_XVIRTUALSCREEN)
            _v_top = user32.GetSystemMetrics(SM_YVIRTUALSCREEN)
            _v_width = user32.GetSystemMetrics(SM_CXVIRTUALSCREEN)
            _v_height = user32.GetSystemMetrics(SM_CYVIRTUALSCREEN)
            _virtual_ok = True
        except Exception:
            _v_left = 0
            _v_top = 0
            _v_width = 1920
            _v_height = 1080

        self.root = tk.Tk()

        # If the Win32 API calls failed, get dimensions from tkinter as fallback
        if not _virtual_ok:
            try:
                _v_width = self.root.winfo_screenwidth()
                _v_height = self.root.winfo_screenheight()
            except Exception:
                pass
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        # Cover the full virtual desktop bounding box instead of just the
        # primary monitor (attributes "-fullscreen" only covers one screen).
        self.root.geometry(f"{_v_width}x{_v_height}+{_v_left}+{_v_top}")
        self.root.configure(bg="#0b0f14")
        self.root.attributes("-alpha", 0.45)  # semi-transparent dim layer
        self.root.config(cursor="crosshair")

        self._canvas = tk.Canvas(
            self.root, highlightthickness=0, cursor="crosshair",
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

        self._start_x: int | None = None
        self._start_y: int | None = None
        self._rect_id: int | None = None
        self.selected: tuple[int, int, int, int] | None = None

        self._canvas.bind("<ButtonPress-1>", self._on_press)
        self._canvas.bind("<B1-Motion>", self._on_drag)
        self._canvas.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", lambda _: self._cancel())

        # Show a hint at the top of the primary monitor
        self._canvas.create_text(
            self.root.winfo_screenwidth() // 2,
            30,
            text="Drag to select a region · Esc to cancel",
            fill="#8b9cb3",
            font=("Segoe UI", 14, "normal"),
            anchor="center",
        )

    def _on_press(self, event: tk.Event) -> None:
        self._start_x = event.x_root
        self._start_y = event.y_root

    def _on_drag(self, event: tk.Event) -> None:
        if self._rect_id:
            self._canvas.delete(self._rect_id)
        self._rect_id = self._canvas.create_rectangle(
            self._start_x, self._start_y,
            event.x_root, event.y_root,
            outline="#3b82f6",
            width=3,
        )

    def _on_release(self, event: tk.Event) -> None:
        if self._start_x is None or self._start_y is None:
            return

        x1 = min(self._start_x, event.x_root)
        y1 = min(self._start_y, event.y_root)
        x2 = max(self._start_x, event.x_root)
        y2 = max(self._start_y, event.y_root)

        if x2 - x1 < 8 or y2 - y1 < 8:
            self._cancel()
            return

        self.selected = (x1, y1, x2, y2)
        self.root.quit()
        self.root.destroy()

    def _cancel(self) -> None:
        self.selected = None
        self.root.quit()
        self.root.destroy()

    def run(self) -> tuple[int, int, int, int] | None:
        """Enter the tkinter event loop and return selected coords or None."""
        # Make sure the overlay is visible and interactive
        self.root.focus_force()
        self.root.mainloop()
        return self.selected


# ── Language picker dialog ─────────────────────────────────────────────────

def _ask_language() -> tuple[str | None, bool]:
    """Show a small, centered, topmost dialog to pick the OCR language.

    Returns:
        A tuple ``(language_code, use_accurate_mode)`` where:

        - ``language_code`` is ``"fas"``, ``"eng"``, ``"fas+eng"``, or
          ``None`` if the user cancels (closes / presses Escape).
        - ``use_accurate_mode`` is ``True`` if the "High Accuracy" checkbox
          was ticked, ``False`` otherwise.
    """
    root = tk.Tk()
    root.title("Select OCR Language")
    root.attributes("-topmost", True)
    root.configure(bg="#141a22")

    result: str | None = None
    accurate_var = tk.BooleanVar(value=False)

    def _pick(value: str) -> None:
        nonlocal result
        result = value
        root.quit()
        root.destroy()

    def _on_close() -> None:
        root.quit()
        root.destroy()

    root.bind("<Escape>", lambda _: _on_close())
    root.protocol("WM_DELETE_WINDOW", _on_close)

    # ── Build UI ───────────────────────────────────────────────────────
    frame = tk.Frame(root, bg="#141a22", padx=20, pady=16)
    frame.pack()

    tk.Label(
        frame,
        text="Select OCR Language / انتخاب زبان",
        bg="#141a22",
        fg="#e8edf4",
        font=("Segoe UI", 12, "bold"),
    ).pack(pady=(0, 12))

    for label, value in [
        ("Persian (فارسی)", "fas"),
        ("English", "eng"),
        ("Both (فارسی + English)", "fas+eng"),
    ]:
        btn = tk.Button(
            frame,
            text=label,
            bg="#3b82f6",
            fg="white",
            activebackground="#2563eb",
            activeforeground="white",
            relief="flat",
            padx=16,
            pady=6,
            font=("Segoe UI", 11),
            cursor="hand2",
            command=lambda v=value: _pick(v),
        )
        btn.pack(fill="x", pady=3)

    # ── High-Accuracy toggle ───────────────────────────────────────────
    tk.Checkbutton(
        frame,
        text="High Accuracy Mode (Slower, better for small/noisy text)",
        variable=accurate_var,
        bg="#141a22",
        fg="#e8edf4",
        activebackground="#141a22",
        activeforeground="#e8edf4",
        selectcolor="#0d1219",
        font=("Segoe UI", 9),
        wraplength=260,
        justify="left",
    ).pack(pady=(8, 0), anchor="w")

    # ── Centre on screen ────────────────────────────────────────────────
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{max(w, 300)}x{max(h, 220)}+{(sw - w) // 2}+{(sh - h) // 2}")

    root.focus_force()
    root.mainloop()

    # If the loop ended without _pick being called, result stays None
    return result, accurate_var.get()


# ── Capture, OCR & typing pipeline ─────────────────────────────────────────

def _capture_region(x1: int, y1: int, x2: int, y2: int) -> Image.Image:
    """Capture the given screen rectangle with *mss* and return a PIL Image."""
    with mss.mss() as sct:
        raw = sct.grab({"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1})
    return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def _ocr_text(
    image: Image.Image,
    lang_override: str | None = None,
    accurate_mode: bool = False,
) -> str:
    """Run OCR on the captured image using the app's OCR pipeline.

    Args:
        image: The PIL image to recognise.
        lang_override: If provided, use this language instead of the
                       module-level ``_lang`` variable.
        accurate_mode: If ``True``, bypass ``_fast_mode`` and run the
                       standard pipeline with full preprocessing and
                       ``psm=6`` — ideal for small or noisy text.
    """
    lang = lang_override if lang_override is not None else _lang

    if accurate_mode:
        # Force high-accuracy pipeline regardless of module-level setting
        from ocr_utils import build_tesseract_config, run_ocr

        return run_ocr(
            image,
            _tesseract_path,
            lang=lang,
            tesseract_config=build_tesseract_config(psm=6, oem=1),
            preprocess=True,
            binarize=True,
            auto_psm=False,
        )

    if _fast_mode:
        from ocr_utils import run_ocr_fast

        return run_ocr_fast(image, _tesseract_path, lang=lang)
    else:
        from ocr_utils import build_tesseract_config, run_ocr

        return run_ocr(
            image,
            _tesseract_path,
            lang=lang,
            tesseract_config=build_tesseract_config(psm=6, oem=1),
            preprocess=True,
            binarize=False,
            auto_psm=False,
        )


def _simulate_typing(text: str) -> None:
    """Inject *text* into the currently focused application.

    Uses clipboard + Ctrl+V for reliable Persian/Unicode support, falling
    back to pyautogui.write() if the clipboard route fails.
    """
    import pyautogui

    try:
        import pyperclip

        original = pyperclip.paste()
        pyperclip.copy(text)
        time.sleep(0.08)
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.15)  # Give slow apps (MS Word, browsers) time to paste
        pyperclip.copy(original)  # restore original clipboard
    except Exception:
        # Fallback: try direct keystroke injection
        pyautogui.write(text, interval=0.005)


def _run_snipping_workflow() -> None:
    """Full snipping pipeline: overlay → capture → OCR → type."""
    if not _tesseract_path:
        return

    overlay = _SnippingOverlay()
    coords = overlay.run()
    if coords is None:
        return  # user cancelled

    # Ask the user which language to use for this snip (and mode preference)
    lang, use_accurate_mode = _ask_language()
    if lang is None:
        return  # user cancelled the language picker

    try:
        image = _capture_region(*coords)
        text = _ocr_text(image, lang_override=lang, accurate_mode=use_accurate_mode)
        if text:
            _simulate_typing(text)
            if _on_text_extracted:
                _on_text_extracted(text, lang)
    except Exception as exc:
        # Log failures for debugging without crashing the background thread
        print(f"[snipping] workflow failed: {exc}")
