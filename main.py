import base64
import ctypes
import os
import sys
import threading
import time
from io import BytesIO

import flet as ft
import fitz
from PIL import Image

from export_utils import save_export
from ocr_utils import build_tesseract_config, get_psm_reason_label, preprocess_image, run_ocr, suggest_psm
from settings import load_settings, save_settings
from tessdata_manager import apply_ocr_mode, ensure_model_store, trim_unused_tessdata

APP_VERSION = "1.5.0"
APP_AUTHOR = "Hamed Gharghi"
APP_GITHUB = "https://github.com/Hamed-Gharghi/Persian-OCR-App"
EXPORT_EXTENSIONS = {"txt": ["txt"], "docx": ["docx"], "pdf": ["pdf"]}
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".pdf"}
PREVIEW_HEIGHT = 220
RESULT_HEIGHT = 300

COLORS = {
    "bg": "#0b0f14",
    "card": "#141a22",
    "card_border": "#243041",
    "primary": "#3b82f6",
    "primary_soft": "#1a2d4a",
    "danger": "#ef4444",
    "text": "#e8edf4",
    "muted": "#8b9cb3",
    "input": "#0d1219",
    "success": "#34d399",
    "info": "#60a5fa",
    "error": "#f87171",
    "log_bg": "#0a0e13",
    "log_row": "#111820",
    "header": "#10161f",
    "accent": "#6366f1",
}

TEXT = {
    "en": {
        "title": f"Persian OCR v{APP_VERSION}",
        "brand": "Persian OCR",
        "version": f"Version {APP_VERSION}",
        "lang_switch": "فارسی",
        "status_default": "Select an image or PDF, then run OCR.",
        "select_file": "Select Image or PDF",
        "preview_empty": "Document preview will appear here",
        "drop_hint": "Or drag and drop a file onto the window",
        "export_format": "Export format",
        "export_txt": "Plain text (.txt)",
        "export_docx": "Word document (.docx)",
        "export_pdf": "PDF (.pdf)",
        "ocr_page_progress": "Processing page {current} of {total}...",
        "saved_searchable_pdf": "Saved searchable PDF: {path}",
        "saved_text_pdf": "Saved text PDF: {path}",
        "settings": "OCR Settings",
        "ocr_lang": "OCR language",
        "page_layout": "Page layout",
        "preprocess": "Enhance image before OCR",
        "binarize": "Binarize (black/white)",
        "auto_psm": "Auto-detect page layout",
        "show_preprocessed": "Show preprocessed preview",
        "psm_suggested": "Layout: PSM {psm} ({reason})",
        "preview_preprocessed": "OCR input preview (preprocessed)",
        "preview_original": "Original preview",
        "page_range": "PDF page range",
        "from_page": "From",
        "to_page": "to",
        "run": "Run OCR",
        "stop": "Stop",
        "save": "Save Output",
        "result": "OCR Result",
        "result_empty": "Recognized text will appear here. You can edit it before saving.",
        "result_stats": "{words} words · {chars} characters · {lines} lines",
        "result_page": "— Page {page} —",
        "copy": "Copy",
        "clear": "Clear",
        "log": "Activity Log",
        "page_nav": "Page {current} / {total}",
        "lang_fas_eng": "Persian + English",
        "lang_fas": "Persian only",
        "psm_3": "Full page (PSM 3)",
        "psm_6": "Single block (PSM 6)",
        "psm_7": "Single line (PSM 7)",
        "psm_11": "Sparse text (PSM 11)",
        "ocr_mode": "Recognition quality",
        "ocr_fast": "Fast (lighter Persian model)",
        "ocr_accurate": "Accurate (best Persian model)",
        "select_folder": "Process Folder",
        "batch_progress": "File {current} of {total}: {name}",
        "batch_done": "Batch OCR complete ({count} files, {elapsed:.1f}s)",
        "shortcuts": "Ctrl+O open · Ctrl+C copy · Ctrl+S save",
        "preview": "Document Preview",
        "actions": "Actions",
        "author_by": "By {name}",
        "author_link": "GitHub",
    },
    "fa": {
        "title": f"برنامه OCR فارسی v{APP_VERSION}",
        "brand": "برنامه OCR فارسی",
        "version": f"نسخه {APP_VERSION}",
        "lang_switch": "English",
        "status_default": "یک تصویر یا PDF انتخاب کنید، سپس OCR را اجرا کنید.",
        "select_file": "انتخاب تصویر یا PDF",
        "preview_empty": "پیش‌نمایش سند اینجا نمایش داده می‌شود",
        "drop_hint": "یا فایل را روی پنجره رها کنید",
        "export_format": "فرمت خروجی",
        "export_txt": "متن ساده (.txt)",
        "export_docx": "سند Word (.docx)",
        "export_pdf": "PDF (.pdf)",
        "ocr_page_progress": "در حال پردازش صفحه {current} از {total}...",
        "saved_searchable_pdf": "PDF قابل جستجو ذخیره شد: {path}",
        "saved_text_pdf": "PDF متنی ذخیره شد: {path}",
        "settings": "تنظیمات OCR",
        "ocr_lang": "زبان OCR",
        "page_layout": "چیدمان صفحه",
        "preprocess": "بهبود تصویر قبل از OCR",
        "binarize": "تبدیل به سیاه و سفید",
        "auto_psm": "تشخیص خودکار چیدمان",
        "show_preprocessed": "نمایش پیش‌نمایش پردازش‌شده",
        "psm_suggested": "چیدمان: PSM {psm} ({reason})",
        "preview_preprocessed": "پیش‌نمایش ورودی OCR (پردازش‌شده)",
        "preview_original": "پیش‌نمایش اصلی",
        "page_range": "محدوده صفحات PDF",
        "from_page": "از",
        "to_page": "تا",
        "run": "اجرای OCR",
        "stop": "توقف",
        "save": "ذخیره خروجی",
        "result": "نتیجه OCR",
        "result_empty": "متن تشخیص‌داده‌شده اینجا نمایش داده می‌شود. قبل از ذخیره می‌توانید ویرایش کنید.",
        "result_stats": "{words} کلمه · {chars} نویسه · {lines} خط",
        "result_page": "— صفحه {page} —",
        "copy": "کپی",
        "clear": "پاک کردن",
        "log": "گزارش فعالیت",
        "page_nav": "صفحه {current} از {total}",
        "lang_fas_eng": "فارسی + انگلیسی",
        "lang_fas": "فقط فارسی",
        "psm_3": "کل صفحه (PSM 3)",
        "psm_6": "یک بلوک (PSM 6)",
        "psm_7": "یک خط (PSM 7)",
        "psm_11": "متن پراکنده (PSM 11)",
        "ocr_mode": "کیفیت تشخیص",
        "ocr_fast": "سریع (مدل سبک فارسی)",
        "ocr_accurate": "دقیق (بهترین مدل فارسی)",
        "select_folder": "پردازش پوشه",
        "batch_progress": "فایل {current} از {total}: {name}",
        "batch_done": "OCR دسته‌ای کامل شد ({count} فایل، {elapsed:.1f} ثانیه)",
        "shortcuts": "Ctrl+O باز کردن · Ctrl+C کپی · Ctrl+S ذخیره",
        "preview": "پیش‌نمایش سند",
        "actions": "عملیات",
        "author_by": "توسط {name}",
        "author_link": "گیت‌هاب",
    },
}


def get_resource_dir():
    if getattr(sys, "frozen", False):
        for base in (getattr(sys, "_MEIPASS", ""), os.path.dirname(sys.executable)):
            if base and os.path.isdir(os.path.join(base, "Tesseract")):
                return base
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def get_asset_path(filename):
    return os.path.join(get_resource_dir(), "assets", filename)


def open_pdf(file_path):
    doc = fitz.open(file_path)
    try:
        catalog = doc.pdf_catalog()
        if catalog:
            doc.xref_set_key(catalog, "StructTreeRoot", "null")
    except Exception:
        pass
    fitz.TOOLS.mupdf_warnings(reset=True)
    return doc


def get_pdf_page_count(file_path):
    doc = open_pdf(file_path)
    count = len(doc)
    doc.close()
    return count


def pdf_to_images(file_path, dpi=300, first_page=None, last_page=None):
    doc = open_pdf(file_path)
    total_pages = len(doc)
    start = max((first_page or 1) - 1, 0)
    end = min((last_page or total_pages) - 1, total_pages - 1)
    zoom = dpi / 72
    matrix = fitz.Matrix(zoom, zoom)
    images = []
    for page_num in range(start, end + 1):
        pix = doc[page_num].get_pixmap(matrix=matrix)
        images.append(Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    doc.close()
    return images


def image_to_base64(image, max_size=(520, PREVIEW_HEIGHT)):
    image = image.copy()
    image.thumbnail(max_size)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


class PersianOCRApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.language = "fa"
        self.file_path = None
        self.is_pdf = False
        self.pdf_page_count = 0
        self.preview_page = 1
        self.cancel_event = threading.Event()
        self.ocr_running = False
        self.batch_files = []

        ensure_model_store()
        trim_unused_tessdata()

        self.tesseract_path = os.path.join(get_resource_dir(), "Tesseract", "tesseract.exe")
        self.page.on_keyboard_event = self._on_keyboard

        self.file_picker = ft.FilePicker()
        self.save_picker = ft.FilePicker()
        self.clipboard = ft.Clipboard()
        self.page.services.extend([self.file_picker, self.save_picker, self.clipboard])

        icon_path = get_asset_path("icon.ico")
        if os.path.isfile(icon_path):
            self.page.window.icon = icon_path

        self._init_controls()
        self._load_saved_settings()
        self._apply_language()
        self._build_layout()
        self._enable_file_drop()

    def t(self, key):
        return TEXT[self.language][key]

    def _init_controls(self):
        self.status_text = ft.Text(self.t("status_default"), color=COLORS["text"], size=13, weight=ft.FontWeight.W_500)
        self.shortcuts_hint = ft.Text(self.t("shortcuts"), color=COLORS["muted"], size=11)
        self.preview_mode_label = ft.Text("", size=11, color=COLORS["muted"])
        self.preview_image = ft.Image(src="", fit=ft.BoxFit.CONTAIN, height=PREVIEW_HEIGHT, visible=False)
        self.preview_placeholder = ft.Column(
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(self.t("preview_empty"), color=COLORS["muted"], size=13),
                ft.Text(self.t("drop_hint"), color=COLORS["muted"], size=11, italic=True),
            ],
        )
        self.preview_page_label = ft.Text("", color=COLORS["muted"], size=13)
        self.preview_nav_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            visible=False,
            controls=[
                ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, on_click=self._prev_preview_page),
                self.preview_page_label,
                ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, on_click=self._next_preview_page),
            ],
        )

        self.lang_dropdown = ft.Dropdown(
            options=[
                ft.DropdownOption(key="fas+eng", text=self.t("lang_fas_eng")),
                ft.DropdownOption(key="fas", text=self.t("lang_fas")),
            ],
            value="fas+eng",
            border_color=COLORS["card_border"],
            bgcolor=COLORS["input"],
            color=COLORS["text"],
            on_select=self._on_settings_changed,
        )
        self.psm_dropdown = ft.Dropdown(
            options=[
                ft.DropdownOption(key="3", text=self.t("psm_3")),
                ft.DropdownOption(key="6", text=self.t("psm_6")),
                ft.DropdownOption(key="7", text=self.t("psm_7")),
                ft.DropdownOption(key="11", text=self.t("psm_11")),
            ],
            value="3",
            border_color=COLORS["card_border"],
            bgcolor=COLORS["input"],
            color=COLORS["text"],
            on_select=self._on_settings_changed,
        )
        self.ocr_mode_dropdown = ft.Dropdown(
            options=[
                ft.DropdownOption(key="accurate", text=self.t("ocr_accurate")),
                ft.DropdownOption(key="fast", text=self.t("ocr_fast")),
            ],
            value="accurate",
            border_color=COLORS["card_border"],
            bgcolor=COLORS["input"],
            color=COLORS["text"],
            on_select=self._on_ocr_mode_changed,
        )
        self.export_dropdown = ft.Dropdown(
            options=[
                ft.DropdownOption(key="txt", text=self.t("export_txt")),
                ft.DropdownOption(key="docx", text=self.t("export_docx")),
                ft.DropdownOption(key="pdf", text=self.t("export_pdf")),
            ],
            value="txt",
            width=220,
            border_color=COLORS["card_border"],
            bgcolor=COLORS["input"],
            color=COLORS["text"],
            on_select=self._on_settings_changed,
        )
        self.preprocess_check = ft.Checkbox(
            label=self.t("preprocess"), value=True, label_style=ft.TextStyle(color=COLORS["text"]),
            on_change=self._on_preview_settings_changed,
        )
        self.binarize_check = ft.Checkbox(
            label=self.t("binarize"), value=False, label_style=ft.TextStyle(color=COLORS["text"]),
            on_change=self._on_preview_settings_changed,
        )
        self.auto_psm_check = ft.Checkbox(
            label=self.t("auto_psm"), value=True, label_style=ft.TextStyle(color=COLORS["text"]),
            on_change=self._on_auto_psm_changed,
        )
        self.show_preprocessed_check = ft.Checkbox(
            label=self.t("show_preprocessed"), value=False, label_style=ft.TextStyle(color=COLORS["text"]),
            on_change=self._on_preview_settings_changed,
        )
        self.psm_hint = ft.Text("", size=12, color=COLORS["info"])
        self.page_from = ft.TextField(value="1", width=80, text_align=ft.TextAlign.CENTER, bgcolor=COLORS["input"], color=COLORS["text"], border_color=COLORS["card_border"])
        self.page_to = ft.TextField(value="1", width=80, text_align=ft.TextAlign.CENTER, bgcolor=COLORS["input"], color=COLORS["text"], border_color=COLORS["card_border"])
        self.page_range_title = ft.Text(self.t("page_range"), color=COLORS["text"], weight=ft.FontWeight.W_600, size=14)
        self.page_from_label = ft.Text(self.t("from_page"), color=COLORS["muted"])
        self.page_to_label = ft.Text(self.t("to_page"), color=COLORS["muted"])
        self.page_range_block = ft.Column(visible=False, spacing=8, controls=[
            self.page_range_title,
            ft.Row([
                self.page_from_label,
                self.page_from,
                self.page_to_label,
                self.page_to,
            ], spacing=8),
        ])
        self.preview_placeholder_box = ft.Container(
            content=self.preview_placeholder,
            alignment=ft.Alignment.CENTER,
            height=PREVIEW_HEIGHT,
        )

        self.progress = ft.ProgressBar(value=0, visible=False, color=COLORS["primary"], bgcolor=COLORS["input"])
        self.progress_label = ft.Text("", size=12, color=COLORS["muted"])
        self.result_stats = ft.Text("", size=12, color=COLORS["muted"])
        self.result_field = ft.TextField(
            multiline=True,
            min_lines=12,
            height=RESULT_HEIGHT,
            text_size=15,
            text_style=ft.TextStyle(height=1.6),
            hint_text=self.t("result_empty"),
            hint_style=ft.TextStyle(color=COLORS["muted"], size=14),
            content_padding=ft.Padding.all(14),
            filled=True,
            fill_color="#0c1118",
            border_radius=8,
            text_align=ft.TextAlign.RIGHT,
            color=COLORS["text"],
            border_color=COLORS["card_border"],
            on_change=self._update_result_stats,
        )
        self.log_list = ft.ListView(spacing=2, height=150, auto_scroll=True, padding=4)
        self.log_panel = ft.Container(
            bgcolor=COLORS["log_bg"],
            border=ft.Border.all(1, COLORS["card_border"]),
            border_radius=10,
            padding=8,
            content=self.log_list,
        )

        self.run_btn = ft.Button(
            self.t("run"), icon=ft.Icons.PLAY_ARROW, bgcolor=COLORS["primary"], color="white",
            height=42, on_click=self._run_ocr, disabled=True,
        )
        self.stop_btn = ft.Button(
            self.t("stop"), icon=ft.Icons.STOP, bgcolor=COLORS["danger"], color="white",
            height=42, on_click=self._stop_ocr, disabled=True,
        )
        self.save_btn = self._outline_button(self.t("save"), ft.Icons.SAVE, self._save_output, disabled=True)
        self.copy_btn = self._outline_button(self.t("copy"), ft.Icons.COPY, self._copy_output, disabled=True)
        self.clear_btn = self._outline_button(self.t("clear"), ft.Icons.CLEAR, self._clear_output, disabled=True)
        self.lang_btn = self._ghost_button(self.t("lang_switch"), self._toggle_language)
        self.author_label = ft.Text(
            self.t("author_by").format(name=APP_AUTHOR),
            size=11,
            color=COLORS["muted"],
        )
        self.github_link = ft.TextButton(
            content=ft.Text(self.t("author_link"), size=11, color=COLORS["primary"]),
            style=ft.ButtonStyle(padding=ft.Padding(0, 0, 0, 0)),
            on_click=self._open_github,
        )
        self.select_file_btn = ft.Button(
            self.t("select_file"), icon=ft.Icons.UPLOAD_FILE, bgcolor=COLORS["primary"], color="white",
            height=44, on_click=self._pick_file,
        )
        self.select_folder_btn = self._outline_button(
            self.t("select_folder"), ft.Icons.FOLDER_OPEN, self._pick_folder, disabled=False,
        )

    def _outline_button(self, label, icon, on_click, disabled=False):
        return ft.Button(
            content=label,
            icon=icon,
            height=40,
            disabled=disabled,
            style=ft.ButtonStyle(
                color=COLORS["text"],
                bgcolor=COLORS["card"],
                side=ft.BorderSide(1, COLORS["card_border"]),
                shape=ft.RoundedRectangleBorder(radius=8),
            ),
            on_click=on_click,
        )

    def _ghost_button(self, label, on_click):
        return ft.Button(
            content=label,
            style=ft.ButtonStyle(color=COLORS["info"], overlay_color=COLORS["primary_soft"]),
            on_click=on_click,
        )

    def _card(self, title, content, padding=16, icon=None):
        header = None
        if title:
            header_controls = []
            if icon:
                header_controls.append(ft.Icon(icon, size=18, color=COLORS["accent"]))
            header_controls.append(ft.Text(title, size=15, weight=ft.FontWeight.W_600, color=COLORS["text"]))
            header = ft.Row(header_controls, spacing=8)
        items = [header, content] if header else [content]
        return ft.Container(
            bgcolor=COLORS["card"],
            border=ft.Border.all(1, COLORS["card_border"]),
            border_radius=14,
            padding=padding,
            content=ft.Column(items, spacing=12),
        )

    def _header_card(self):
        return ft.Container(
            bgcolor=COLORS["header"],
            border=ft.Border.all(1, COLORS["card_border"]),
            border_radius=14,
            padding=ft.Padding.symmetric(horizontal=18, vertical=14),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                width=42, height=42, border_radius=10, bgcolor=COLORS["primary_soft"],
                                alignment=ft.Alignment.CENTER,
                                content=ft.Icon(ft.Icons.DOCUMENT_SCANNER, color=COLORS["primary"], size=22),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(self.t("brand"), size=22, weight=ft.FontWeight.BOLD, color=COLORS["text"]),
                                    ft.Text(self.t("version"), size=12, color=COLORS["muted"]),
                                    ft.Row(
                                        spacing=6,
                                        controls=[self.author_label, self.github_link],
                                    ),
                                ],
                            ),
                        ],
                    ),
                    self.lang_btn,
                ],
            ),
        )

    def _setting_block(self, label, control):
        return ft.Column(
            spacing=6,
            controls=[
                ft.Text(label, size=14, weight=ft.FontWeight.W_600, color=COLORS["text"]),
                control,
            ],
        )

    def _load_saved_settings(self):
        settings = load_settings()
        self.language = settings.get("ui_language", "fa")
        self.lang_dropdown.value = settings.get("ocr_lang", "fas+eng")
        self.psm_dropdown.value = str(settings.get("psm", "3"))
        self.preprocess_check.value = bool(settings.get("preprocess", True))
        self.binarize_check.value = bool(settings.get("binarize", False))
        self.auto_psm_check.value = bool(settings.get("auto_psm", True))
        self.show_preprocessed_check.value = bool(settings.get("show_preprocessed", False))
        self.export_dropdown.value = settings.get("export_format", "txt")
        self.ocr_mode_dropdown.value = settings.get("ocr_mode", "accurate")
        apply_ocr_mode(self.ocr_mode_dropdown.value)

    def _persist_settings(self):
        save_settings({
            "ui_language": self.language,
            "ocr_lang": self.lang_dropdown.value,
            "psm": self.psm_dropdown.value,
            "preprocess": self.preprocess_check.value,
            "binarize": self.binarize_check.value,
            "auto_psm": self.auto_psm_check.value,
            "show_preprocessed": self.show_preprocessed_check.value,
            "export_format": self.export_dropdown.value,
            "ocr_mode": self.ocr_mode_dropdown.value,
        })

    def _on_settings_changed(self, _=None):
        self._persist_settings()

    def _on_ocr_mode_changed(self, _=None):
        apply_ocr_mode(self.ocr_mode_dropdown.value or "accurate")
        self._persist_settings()
        self._log(
            self.t("ocr_fast") if self.ocr_mode_dropdown.value == "fast" else self.t("ocr_accurate"),
            "info",
        )
        self.page.update()

    def _build_preview_card(self):
        return ft.Column(
            [
                self.preview_mode_label,
                self.preview_image,
                self.preview_placeholder_box,
                self.preview_nav_row,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_layout(self):
        settings_content = ft.Column(
            spacing=14,
            controls=[
                self._setting_block(self.t("ocr_lang"), self.lang_dropdown),
                self._setting_block(self.t("ocr_mode"), self.ocr_mode_dropdown),
                self._setting_block(self.t("page_layout"), self.psm_dropdown),
                self.auto_psm_check,
                self.psm_hint,
                self.preprocess_check,
                self.binarize_check,
                self.show_preprocessed_check,
                self.page_range_block,
            ],
        )

        self.page.controls.clear()
        self.page.add(
            ft.Column(
                expand=True,
                scroll=ft.ScrollMode.AUTO,
                spacing=14,
                controls=[
                    self._header_card(),
                    self._card("", ft.Column([
                        self.status_text,
                        self.shortcuts_hint,
                    ], spacing=6), padding=14),
                    self._card(self.t("actions"), ft.Row(
                        [self.select_file_btn, self.select_folder_btn],
                        spacing=10,
                        wrap=True,
                    ), padding=14, icon=ft.Icons.TOUCH_APP),
                    self._card(self.t("preview"), self._build_preview_card(), padding=12, icon=ft.Icons.IMAGE),
                    self._card(self.t("settings"), settings_content, icon=ft.Icons.TUNE),
                    ft.Row([self.run_btn, self.stop_btn], spacing=10),
                    ft.Row(
                        [self._setting_block(self.t("export_format"), self.export_dropdown), self.save_btn],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    self.progress,
                    self.progress_label,
                    self._card(self.t("result"), ft.Column([
                        ft.Row(
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                self.result_stats,
                                ft.Row([self.copy_btn, self.clear_btn], spacing=8),
                            ],
                        ),
                        self.result_field,
                    ], spacing=10), icon=ft.Icons.ARTICLE),
                    self._card(self.t("log"), self.log_panel, icon=ft.Icons.HISTORY),
                ],
            )
        )

    def _apply_language(self):
        self.page.rtl = self.language == "fa"
        self.page.title = self.t("title")
        self.page.bgcolor = COLORS["bg"]
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 18
        self.page.window.width = 820
        self.page.window.height = 940
        self.page.window.min_width = 700
        self.page.window.min_height = 760

        align = ft.TextAlign.RIGHT if self.language == "fa" else ft.TextAlign.LEFT
        self.result_field.text_align = align

    def _refresh_texts(self):
        self.status_text.value = self.t("status_default")
        self.preview_placeholder.controls[0].value = self.t("preview_empty")
        self.preview_placeholder.controls[1].value = self.t("drop_hint")
        self.export_dropdown.label = self.t("export_format")
        self.export_dropdown.options = [
            ft.DropdownOption(key="txt", text=self.t("export_txt")),
            ft.DropdownOption(key="docx", text=self.t("export_docx")),
            ft.DropdownOption(key="pdf", text=self.t("export_pdf")),
        ]
        self.lang_dropdown.label = self.t("ocr_lang")
        self.lang_dropdown.options = [
            ft.DropdownOption(key="fas+eng", text=self.t("lang_fas_eng")),
            ft.DropdownOption(key="fas", text=self.t("lang_fas")),
        ]
        self.psm_dropdown.label = self.t("page_layout")
        self.psm_dropdown.options = [
            ft.DropdownOption(key="3", text=self.t("psm_3")),
            ft.DropdownOption(key="6", text=self.t("psm_6")),
            ft.DropdownOption(key="7", text=self.t("psm_7")),
            ft.DropdownOption(key="11", text=self.t("psm_11")),
        ]
        self.preprocess_check.label = self.t("preprocess")
        self.binarize_check.label = self.t("binarize")
        self.auto_psm_check.label = self.t("auto_psm")
        self.show_preprocessed_check.label = self.t("show_preprocessed")
        self.page_range_title.value = self.t("page_range")
        self.page_from_label.value = self.t("from_page")
        self.page_to_label.value = self.t("to_page")
        self.run_btn.content = self.t("run")
        self.stop_btn.content = self.t("stop")
        self.save_btn.content = self.t("save")
        self.copy_btn.content = self.t("copy")
        self.clear_btn.content = self.t("clear")
        self.lang_btn.content = self.t("lang_switch")
        self.author_label.value = self.t("author_by").format(name=APP_AUTHOR)
        self.github_link.content = ft.Text(self.t("author_link"), size=11, color=COLORS["primary"])
        self.select_file_btn.content = self.t("select_file")
        self.select_folder_btn.content = self.t("select_folder")
        self.shortcuts_hint.value = self.t("shortcuts")
        self.ocr_mode_dropdown.label = self.t("ocr_mode")
        self.ocr_mode_dropdown.options = [
            ft.DropdownOption(key="accurate", text=self.t("ocr_accurate")),
            ft.DropdownOption(key="fast", text=self.t("ocr_fast")),
        ]
        self.result_field.hint_text = self.t("result_empty")
        self._update_result_stats()
        if self.file_path and self.auto_psm_check.value:
            self._suggest_psm_for_file(log=False)
        if self.file_path:
            self._render_preview()
        if self.pdf_page_count:
            self._update_preview_nav()

    async def _open_github(self, _):
        await self.page.url_launcher.launch_url(APP_GITHUB)

    def _toggle_language(self, _):
        self.language = "en" if self.language == "fa" else "fa"
        self._apply_language()
        self._refresh_texts()
        self._build_layout()
        self._enable_file_drop()
        self._persist_settings()
        self.page.update()

    def _on_keyboard(self, e: ft.KeyboardEvent):
        if not e.ctrl:
            return
        key = (e.key or "").lower().replace("key ", "")
        if key == "o":
            self.page.run_task(self._pick_file, None)
        elif key == "c":
            self.page.run_task(self._copy_output, None)
        elif key == "s":
            self.page.run_task(self._save_output, None)

    def _collect_folder_files(self, folder):
        files = []
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if os.path.isfile(path) and self._is_supported_file(path):
                files.append(path)
        return files

    async def _pick_file(self, _):
        files = await self.file_picker.pick_files(
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["png", "jpg", "jpeg", "bmp", "pdf"],
        )
        if files and files[0].path:
            self.batch_files = []
            self._load_file(files[0].path)

    async def _pick_folder(self, _):
        folder = await self.file_picker.get_directory_path()
        if not folder:
            return
        files = self._collect_folder_files(folder)
        if not files:
            self._log(
                "فایل پشتیبانی‌شده‌ای یافت نشد." if self.language == "fa" else "No supported files found.",
                "error",
            )
            self.page.update()
            return
        self.batch_files = files
        self._log(
            f"{'پوشه انتخاب شد' if self.language == 'fa' else 'Folder selected'}: {len(files)} "
            f"{'فایل' if self.language == 'fa' else 'files'}",
            "info",
        )
        self._start_ocr(batch_files=files)
        self.page.update()

    def _is_supported_file(self, file_path):
        return os.path.splitext(file_path)[1].lower() in SUPPORTED_EXTENSIONS

    def _enable_file_drop(self):
        if sys.platform != "win32":
            return

        def hook():
            import windnd

            for _ in range(30):
                time.sleep(0.2)
                hwnd = ctypes.windll.user32.FindWindowW(None, self.page.title)
                if hwnd:
                    windnd.hook_dropfiles(hwnd, func=self._on_window_files_dropped)
                    return

        threading.Thread(target=hook, daemon=True).start()

    def _on_window_files_dropped(self, files):
        for raw in files:
            path = raw.decode("mbcs") if isinstance(raw, bytes) else str(raw)
            if self._is_supported_file(path):
                self.page.run_task(self._load_file_async, path)
                return

    async def _load_file_async(self, file_path):
        self._load_file(file_path)

    def _load_file(self, file_path):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        self.is_pdf = ext == ".pdf"
        self.preview_page = 1
        name = os.path.basename(file_path)

        if self.is_pdf:
            self.pdf_page_count = get_pdf_page_count(file_path)
            self.page_from.value = "1"
            self.page_to.value = str(self.pdf_page_count)
            self.page_range_block.visible = True
            self.preview_nav_row.visible = True
            self._update_preview_nav()
            self.status_text.value = f"{'PDF انتخاب شد' if self.language == 'fa' else 'PDF selected'}: {name}"
            self._log(f"{'PDF انتخاب شد' if self.language == 'fa' else 'Selected PDF'}: {name}", "info")
        else:
            self.pdf_page_count = 0
            self.page_range_block.visible = False
            self.preview_nav_row.visible = False
            self.status_text.value = f"{'تصویر انتخاب شد' if self.language == 'fa' else 'Image selected'}: {name}"
            self._log(f"{'تصویر انتخاب شد' if self.language == 'fa' else 'Selected image'}: {name}", "info")

        self._suggest_psm_for_file()
        self._render_preview()
        self.run_btn.disabled = False
        self.save_btn.disabled = True
        self.copy_btn.disabled = True
        self.clear_btn.disabled = True
        self.result_field.value = ""
        self._update_result_stats()
        self.progress.visible = False
        self.page.update()

    def _get_source_image(self, for_preview=False):
        if not self.file_path:
            return None
        if self.is_pdf:
            images = pdf_to_images(
                self.file_path, dpi=120,
                first_page=self.preview_page, last_page=self.preview_page,
            )
            return images[0] if images else None
        with Image.open(self.file_path) as img:
            return img.copy()

    def _suggest_psm_for_file(self, log=True):
        if not self.auto_psm_check.value or not self.file_path:
            self.psm_hint.value = ""
            return
        try:
            image = self._get_source_image(for_preview=True)
            if not image:
                return
            psm, reason = suggest_psm(image)
            self.psm_dropdown.value = str(psm)
            reason_label = get_psm_reason_label(reason, self.language)
            self.psm_hint.value = self.t("psm_suggested").format(psm=psm, reason=reason_label)
            self._persist_settings()
            if log:
                self._log(self.psm_hint.value, "info")
        except Exception:
            self.psm_hint.value = ""

    def _on_auto_psm_changed(self, _):
        if self.auto_psm_check.value:
            self._suggest_psm_for_file()
        else:
            self.psm_hint.value = ""
        self._persist_settings()
        self.page.update()

    def _on_preview_settings_changed(self, _):
        self._persist_settings()
        if self.file_path:
            self._render_preview()
            self.page.update()

    def _render_preview(self):
        if not self.file_path:
            return
        try:
            image = self._get_source_image(for_preview=True)
            if not image:
                raise ValueError("no image")
            show_processed = self.show_preprocessed_check.value and self.preprocess_check.value
            if show_processed:
                image = preprocess_image(
                    image,
                    binarize=self.binarize_check.value,
                    upscale=True,
                )
                self.preview_mode_label.value = self.t("preview_preprocessed")
            else:
                self.preview_mode_label.value = self.t("preview_original")
            self.preview_image.src = image_to_base64(image)
            self.preview_image.visible = True
            self.preview_placeholder_box.visible = False
        except Exception:
            self.preview_image.visible = False
            self.preview_placeholder_box.visible = True
            self.preview_mode_label.value = ""

    def _update_preview_nav(self):
        self.preview_page_label.value = self.t("page_nav").format(current=self.preview_page, total=max(self.pdf_page_count, 1))

    def _prev_preview_page(self, _):
        if self.preview_page > 1:
            self.preview_page -= 1
            self._update_preview_nav()
            if self.auto_psm_check.value:
                self._suggest_psm_for_file()
            self._render_preview()
            self.page.update()

    def _next_preview_page(self, _):
        if self.preview_page < self.pdf_page_count:
            self.preview_page += 1
            self._update_preview_nav()
            if self.auto_psm_check.value:
                self._suggest_psm_for_file()
            self._render_preview()
            self.page.update()

    def _update_result_stats(self, _=None):
        text = self.result_field.value or ""
        stripped = text.strip()
        if not stripped:
            self.result_stats.value = ""
            return
        self.result_stats.value = self.t("result_stats").format(
            words=len(stripped.split()),
            chars=len(text),
            lines=len(text.splitlines()),
        )

    def _log(self, message, level="info"):
        icons = {
            "info": ft.Icons.INFO_OUTLINED,
            "success": ft.Icons.CHECK_CIRCLE_OUTLINE,
            "error": ft.Icons.ERROR_OUTLINE,
        }
        colors = {"info": COLORS["info"], "success": COLORS["success"], "error": COLORS["error"]}
        stamp = time.strftime("%H:%M:%S")
        entry = ft.Container(
            bgcolor=COLORS["log_row"],
            border_radius=8,
            padding=ft.Padding.symmetric(horizontal=10, vertical=6),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Text(stamp, size=11, color=COLORS["muted"], width=58),
                    ft.Icon(icons.get(level, ft.Icons.INFO_OUTLINED), size=15, color=colors.get(level, COLORS["text"])),
                    ft.Text(message, size=12, color=colors.get(level, COLORS["text"]), expand=True),
                ],
            ),
        )
        self.log_list.controls.append(entry)
        if len(self.log_list.controls) > 80:
            self.log_list.controls.pop(0)

    def _get_options(self):
        return {
            "lang": self.lang_dropdown.value,
            "tesseract_config": build_tesseract_config(psm=int(self.psm_dropdown.value)),
            "preprocess": self.preprocess_check.value,
            "binarize": self.binarize_check.value,
            "auto_psm": self.auto_psm_check.value,
            "page_from": int(self.page_from.value or 1),
            "page_to": int(self.page_to.value or 1),
        }

    def _run_ocr(self, _):
        if not self.file_path or self.ocr_running:
            return
        self._start_ocr()

    def _start_ocr(self, batch_files=None):
        if self.ocr_running:
            return
        options = self._get_options()
        options["batch_files"] = batch_files or []
        if not options["batch_files"] and not self.file_path:
            return
        if not options["batch_files"] and options["page_from"] > options["page_to"]:
            self._log("محدوده صفحات نامعتبر است." if self.language == "fa" else "Invalid page range.", "error")
            self.page.update()
            return

        self.ocr_running = True
        self.cancel_event.clear()
        self.run_btn.disabled = True
        self.stop_btn.disabled = False
        self.save_btn.disabled = True
        self.copy_btn.disabled = True
        self.clear_btn.disabled = True
        self.result_field.value = ""
        self._update_result_stats()
        self.progress.visible = True
        self.progress.value = 0
        self.progress_label.value = ""
        self.status_text.value = "در حال اجرای OCR ..." if self.language == "fa" else "Running OCR..."
        self._log("شروع OCR ..." if self.language == "fa" else "Starting OCR...", "info")
        self.page.update()

        threading.Thread(target=self._ocr_worker, args=(options,), daemon=True).start()

    def _ocr_single_file(self, file_path, options):
        ext = os.path.splitext(file_path)[1].lower()
        parts = []

        if ext == ".pdf":
            images = pdf_to_images(
                file_path, dpi=300,
                first_page=options["page_from"], last_page=options["page_to"],
            )
            for i, img in enumerate(images):
                if self.cancel_event.is_set():
                    break
                page_num = options["page_from"] + i
                text = run_ocr(
                    img, self.tesseract_path,
                    lang=options["lang"],
                    tesseract_config=options["tesseract_config"],
                    preprocess=options["preprocess"],
                    binarize=options["binarize"],
                    auto_psm=options["auto_psm"],
                )
                parts.append(f"\n{self.t('result_page').format(page=page_num)}\n{text}")
        else:
            with Image.open(file_path) as img:
                parts.append(run_ocr(
                    img, self.tesseract_path,
                    lang=options["lang"],
                    tesseract_config=options["tesseract_config"],
                    preprocess=options["preprocess"],
                    binarize=options["binarize"],
                    auto_psm=options["auto_psm"],
                ))
        return "\n".join(parts)

    def _ocr_worker(self, options):
        try:
            start = time.time()
            batch_files = options.get("batch_files") or []

            if batch_files:
                all_text = []
                total = len(batch_files)
                for idx, file_path in enumerate(batch_files):
                    if self.cancel_event.is_set():
                        break
                    name = os.path.basename(file_path)
                    self.page.run_task(self._update_batch_progress, idx, total, name)
                    file_text = self._ocr_single_file(file_path, options)
                    all_text.append(f"\n=== {name} ===\n{file_text}")
                    self.page.run_task(self._update_batch_progress, idx + 1, total, name)
                result = "\n".join(all_text)
                elapsed = time.time() - start
                self.page.run_task(self._finish_ocr, result, self.cancel_event.is_set(), elapsed, total)
                return

            ext = os.path.splitext(self.file_path)[1].lower()
            all_text = []

            if ext == ".pdf":
                images = pdf_to_images(
                    self.file_path, dpi=300,
                    first_page=options["page_from"], last_page=options["page_to"],
                )
                total = len(images)
                for i, img in enumerate(images):
                    if self.cancel_event.is_set():
                        self.page.run_task(self._finish_ocr, "\n".join(all_text), True, time.time() - start)
                        return
                    page_num = options["page_from"] + i
                    self.page.run_task(self._update_progress, i / total, page_num, total)
                    text = run_ocr(
                        img, self.tesseract_path,
                        lang=options["lang"],
                        tesseract_config=options["tesseract_config"],
                        preprocess=options["preprocess"],
                        binarize=options["binarize"],
                        auto_psm=options["auto_psm"],
                    )
                    all_text.append(f"\n{self.t('result_page').format(page=page_num)}\n{text}")
                    self.page.run_task(self._update_progress, (i + 1) / total, page_num, total)
                result = "\n".join(all_text)
            else:
                if self.cancel_event.is_set():
                    self.page.run_task(self._finish_ocr, "", True, time.time() - start)
                    return
                with Image.open(self.file_path) as img:
                    result = run_ocr(
                        img, self.tesseract_path,
                        lang=options["lang"],
                        tesseract_config=options["tesseract_config"],
                        preprocess=options["preprocess"],
                        binarize=options["binarize"],
                        auto_psm=options["auto_psm"],
                    )
                self.page.run_task(self._update_progress, 1.0)

            elapsed = time.time() - start
            self.page.run_task(self._finish_ocr, result, False, elapsed)
        except Exception as exc:
            self.page.run_task(self._ocr_failed, str(exc))

    async def _update_progress(self, value, current_page=None, total_pages=None):
        self.progress.value = value
        if current_page and total_pages:
            self.progress_label.value = self.t("ocr_page_progress").format(
                current=current_page, total=total_pages,
            )
        self.page.update()

    async def _update_batch_progress(self, current, total, name):
        self.progress.value = current / max(total, 1)
        self.progress_label.value = self.t("batch_progress").format(
            current=min(current + 1, total), total=total, name=name,
        )
        self.page.update()

    async def _finish_ocr(self, text, cancelled, elapsed, batch_count=0):
        self.ocr_running = False
        self.run_btn.disabled = False
        self.stop_btn.disabled = True
        self.progress.visible = False
        self.progress_label.value = ""

        if cancelled:
            if text.strip():
                self.result_field.value = text
                self.status_text.value = "OCR متوقف شد. نتیجه جزئی حفظ شد." if self.language == "fa" else "OCR cancelled. Partial result kept."
                self._log(f"OCR متوقف شد ({elapsed:.1f}s)" if self.language == "fa" else f"OCR cancelled ({elapsed:.1f}s)", "info")
                self.save_btn.disabled = False
            else:
                self.status_text.value = "OCR متوقف شد." if self.language == "fa" else "OCR cancelled."
                self._log("OCR متوقف شد." if self.language == "fa" else "OCR cancelled.", "info")
        else:
            self.result_field.value = text
            self.status_text.value = "OCR با موفقیت انجام شد." if self.language == "fa" else "OCR complete."
            if batch_count:
                self._log(self.t("batch_done").format(count=batch_count, elapsed=elapsed), "success")
            else:
                self._log(f"OCR کامل شد ({elapsed:.1f}s)" if self.language == "fa" else f"OCR complete ({elapsed:.1f}s)", "success")
            self.save_btn.disabled = not bool(text.strip())

        has_text = bool(self.result_field.value.strip())
        self.copy_btn.disabled = not has_text
        self.clear_btn.disabled = not has_text
        self._update_result_stats()
        self.page.update()

    async def _ocr_failed(self, message):
        self.ocr_running = False
        self.run_btn.disabled = False
        self.stop_btn.disabled = True
        self.progress.visible = False
        self.progress_label.value = ""
        self.status_text.value = "خطا در اجرای OCR." if self.language == "fa" else "OCR failed."
        self._log(f"OCR failed: {message}", "error")
        self.page.update()

    def _stop_ocr(self, _):
        if self.ocr_running:
            self.cancel_event.set()
            self._log("در حال توقف OCR ..." if self.language == "fa" else "Stopping OCR...", "info")
            self.page.update()

    async def _copy_output(self, _):
        text = self.result_field.value.strip()
        if not text:
            return
        await self.clipboard.set(text)
        self._log("در کلیپ‌بورد کپی شد." if self.language == "fa" else "Copied to clipboard.", "success")
        self.page.update()

    def _clear_output(self, _):
        self.result_field.value = ""
        self.copy_btn.disabled = True
        self.clear_btn.disabled = True
        self.save_btn.disabled = True
        self._update_result_stats()
        self._log("نتیجه OCR پاک شد." if self.language == "fa" else "OCR result cleared.", "info")
        self.page.update()

    async def _save_output(self, _):
        if not self.result_field.value.strip():
            return
        export_fmt = self.export_dropdown.value or "txt"
        extensions = EXPORT_EXTENSIONS.get(export_fmt, ["txt"])
        path = await self.save_picker.save_file(
            file_name=f"output.{extensions[0]}",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=extensions,
        )
        if not path:
            return
        try:
            source_image = None
            if export_fmt == "pdf" and self.file_path and not self.is_pdf:
                source_image = self._get_source_image(for_preview=False)
                if source_image and self.preprocess_check.value:
                    source_image = preprocess_image(
                        source_image,
                        binarize=self.binarize_check.value,
                        upscale=True,
                    )
            result_kind = save_export(
                path,
                self.result_field.value,
                export_fmt,
                source_image=source_image,
                tesseract_path=self.tesseract_path,
                lang=self.lang_dropdown.value,
                tesseract_config=build_tesseract_config(psm=int(self.psm_dropdown.value)),
            )
            if result_kind == "pdf_searchable":
                msg = self.t("saved_searchable_pdf").format(path=path)
            elif result_kind == "pdf_text":
                msg = self.t("saved_text_pdf").format(path=path)
            else:
                msg = (
                    f"خروجی ذخیره شد: {path}" if self.language == "fa" else f"Saved to: {path}"
                )
            self._log(msg, "success")
            self.page.update()
        except Exception as exc:
            self._log(f"Save failed: {exc}", "error")
            self.page.update()


async def main(page: ft.Page):
    PersianOCRApp(page)


if __name__ == "__main__":
    ft.run(main)
