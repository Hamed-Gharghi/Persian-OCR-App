"""
Snipping to Live Typing module for Persian OCR App.

Provides a globally accessible screen-snipping overlay triggered via
Win + Shift + D that captures a screen region, runs OCR, and
auto-types the extracted Persian text into the focused application.
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

_lang: str = "fas+eng"
_mode: str = "accurate"
_on_start: Callable | None = None
_on_end: Callable | None = None
_on_text_extracted: Callable[[str, str], None] | None = None
_on_ocr_progress: Callable[[float, str], None] | None = None
_on_ocr_busy: Callable[[bool], None] | None = None
_lock: Lock = Lock()
_snipping_active: bool = False


def configure(
    *,
    lang: str = "fas+eng",
    mode: str = "accurate",
    on_start: Callable | None = None,
    on_end: Callable | None = None,
    on_text_extracted: Callable[[str, str], None] | None = None,
    on_ocr_progress: Callable[[float, str], None] | None = None,
    on_ocr_busy: Callable[[bool], None] | None = None,
    **_ignored,
) -> None:
    """Pass OCR settings from the main app to the snipping tool.

    Args:
        lang: OCR language string (default "fas+eng").
        mode: "fast" (lighter preprocess) or "accurate" (more detail for small text).
        on_start: Optional callback invoked just before the snipping overlay
                  appears (e.g. to minimise the main window).
        on_end: Optional callback invoked after snipping completes or is
                cancelled (e.g. to restore the main window).
        on_text_extracted: Optional callback invoked after OCR extracts text
                           from the snipped region, receiving the text string and
                           the chosen language code.
        on_ocr_progress: Optional callback(fraction, detail) during snip OCR.
        on_ocr_busy: Optional callback(True/False) when snip OCR starts/ends.
    """
    global _lang, _mode, _on_start, _on_end, _on_text_extracted
    global _on_ocr_progress, _on_ocr_busy
    _lang = lang
    _mode = mode or "accurate"
    if on_start is not None:
        _on_start = on_start
    if on_end is not None:
        _on_end = on_end
    if on_text_extracted is not None:
        _on_text_extracted = on_text_extracted
    if on_ocr_progress is not None:
        _on_ocr_progress = on_ocr_progress
    if on_ocr_busy is not None:
        _on_ocr_busy = on_ocr_busy


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

def _ask_language() -> str | None:
    """Show a small dialog to pick the OCR language. Returns None if cancelled."""
    root = tk.Tk()
    root.title("Select OCR Language")
    root.attributes("-topmost", True)
    root.configure(bg="#141a22")

    result: str | None = None

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

    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    root.geometry(f"{max(w, 300)}x{max(h, 180)}+{(sw - w) // 2}+{(sh - h) // 2}")

    root.focus_force()
    root.mainloop()
    return result


# ── Capture, OCR & typing pipeline ─────────────────────────────────────────

def _capture_region(x1: int, y1: int, x2: int, y2: int) -> Image.Image:
    """Capture the given screen rectangle with *mss* and return a PIL Image."""
    with mss.mss() as sct:
        raw = sct.grab({"top": y1, "left": x1, "width": x2 - x1, "height": y2 - y1})
    return Image.frombytes("RGB", raw.size, raw.bgra, "raw", "BGRX")


def _format_eta(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "estimating… / در حال برآورد…"
    total = int(round(seconds))
    if total < 60:
        return f"~{total}s left / حدود {total} ثانیه"
    minutes, secs = divmod(total, 60)
    return f"~{minutes}:{secs:02d} left / حدود {minutes}:{secs:02d}"


def _stage_label(stage: str) -> str:
    stage = (stage or "").strip().lower()
    if stage.startswith("prepare"):
        return "Preparing… / آماده‌سازی…"
    if stage.startswith("pass"):
        parts = stage.replace("pass", "").strip().split("/")
        try:
            cur, total = parts[0].strip(), parts[1].strip()
            return f"Recognizing ({cur}/{total}) / تشخیص ({cur}/{total})"
        except Exception:
            return "Recognizing… / در حال تشخیص…"
    if stage.startswith("merge") or stage.startswith("done"):
        return "Finishing… / در حال اتمام…"
    return "Running OCR… / در حال OCR…"


class _OcrProgressWindow:
    """Always-on-top progress UI shown while snip OCR runs."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Persian OCR")
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#141a22")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        self._start = time.time()
        self._fraction = 0.0
        self._closed = False

        frame = tk.Frame(self.root, bg="#141a22", padx=22, pady=18)
        frame.pack()

        tk.Label(
            frame,
            text="Screenshot OCR / OCR تصویر",
            bg="#141a22",
            fg="#e8edf4",
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        self.percent_label = tk.Label(
            frame, text="0%", bg="#141a22", fg="#60a5fa",
            font=("Segoe UI", 16, "bold"),
        )
        self.percent_label.pack(anchor="w", pady=(10, 2))

        self.detail_label = tk.Label(
            frame,
            text="Starting… / شروع…",
            bg="#141a22",
            fg="#94a3b8",
            font=("Segoe UI", 10),
            wraplength=320,
            justify="left",
        )
        self.detail_label.pack(anchor="w")

        self.eta_label = tk.Label(
            frame,
            text=_format_eta(None),
            bg="#141a22",
            fg="#38bdf8",
            font=("Segoe UI", 10),
        )
        self.eta_label.pack(anchor="w", pady=(4, 10))

        self.canvas = tk.Canvas(
            frame, width=320, height=12, bg="#0c1118",
            highlightthickness=0, bd=0,
        )
        self.canvas.pack(fill="x")
        self._bar_bg = self.canvas.create_rectangle(0, 0, 320, 12, fill="#1e293b", outline="")
        self._bar_fg = self.canvas.create_rectangle(0, 0, 0, 12, fill="#3b82f6", outline="")

        self.root.update_idletasks()
        w, h = self.root.winfo_width(), self.root.winfo_height()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{max(w, 360)}x{max(h, 160)}+{(sw - w) // 2}+{(sh - h) // 2}")

    def set_progress(self, fraction: float, stage: str = "") -> None:
        if self._closed:
            return
        fraction = max(0.0, min(1.0, float(fraction)))
        self._fraction = fraction
        # Avoid a lingering "Finishing" label — close happens right after OCR returns
        if (stage or "").strip().lower().startswith("done"):
            stage = "merge"

        def _apply() -> None:
            if self._closed:
                return
            pct = int(round(fraction * 100))
            self.percent_label.config(text=f"{pct}%")
            self.detail_label.config(text=_stage_label(stage))
            elapsed = time.time() - self._start
            eta = None
            if fraction >= 0.999:
                eta = 0.0
            elif fraction > 0.08 and elapsed > 0.4:
                eta = elapsed * (1.0 - fraction) / max(fraction, 0.01)
            self.eta_label.config(text=_format_eta(eta))
            self.canvas.coords(self._bar_fg, 0, 0, 320 * fraction, 12)
            if _on_ocr_progress:
                try:
                    _on_ocr_progress(fraction, _stage_label(stage))
                except Exception:
                    pass

        try:
            self.root.after(0, _apply)
        except Exception:
            pass

    def finish(self) -> None:
        self._closed = True

        def _close() -> None:
            try:
                self.root.quit()
            except Exception:
                pass
            try:
                self.root.destroy()
            except Exception:
                pass

        try:
            self.root.after(0, _close)
            # Nudge the event loop in case quit alone is delayed
            self.root.after(50, _close)
        except Exception:
            _close()

    def run(self) -> None:
        self.root.focus_force()
        self.root.mainloop()


def _ocr_text(image: Image.Image, lang_override: str | None = None) -> str:
    """Run OCR on the captured image with a visible progress window."""
    from ocr_utils import run_ocr

    lang = lang_override if lang_override is not None else _lang
    progress = _OcrProgressWindow()
    box: dict = {"text": "", "error": None}

    def work() -> None:
        try:
            if _on_ocr_busy:
                try:
                    _on_ocr_busy(True)
                except Exception:
                    pass
            progress.set_progress(0.02, "prepare")
            box["text"] = run_ocr(
                image,
                lang=lang,
                mode=_mode,
                progress_cb=progress.set_progress,
            )
        except Exception as exc:
            box["error"] = exc
        finally:
            # Close progress UI first so it cannot stick on "Finishing"
            progress.finish()
            if _on_ocr_busy:
                try:
                    _on_ocr_busy(False)
                except Exception:
                    pass

    threading.Thread(target=work, daemon=True).start()
    progress.run()
    if box["error"] is not None:
        raise box["error"]
    return box["text"] or ""


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
    overlay = _SnippingOverlay()
    coords = overlay.run()
    if coords is None:
        return  # user cancelled

    lang = _ask_language()
    if lang is None:
        return  # user cancelled the language picker

    # Restore main window so its progress bar is visible during OCR
    if _on_end:
        try:
            _on_end()
        except Exception:
            pass

    try:
        image = _capture_region(*coords)
        text = _ocr_text(image, lang_override=lang)
        if text:
            _simulate_typing(text)
            if _on_text_extracted:
                _on_text_extracted(text, lang)
    except Exception as exc:
        # Log failures for debugging without crashing the background thread
        print(f"[snipping] workflow failed: {exc}")
