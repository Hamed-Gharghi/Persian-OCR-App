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
from ocr_utils import OCRCancelled, run_ocr, warm_reader
from settings import load_settings, save_settings

import snipping_tool

APP_VERSION = "1.7.0"
APP_AUTHOR = "Hamed Gharghi"
APP_GITHUB = "https://github.com/Hamed-Gharghi/Persian-OCR-App"
EXPORT_EXTENSIONS = {"txt": ["txt"], "docx": ["docx"], "pdf": ["pdf"]}
SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".pdf"}
PREVIEW_HEIGHT = 220
RESULT_HEIGHT = 340
RESULT_WIDTH = 1120

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
        "ocr_progress": "{percent}% complete · {detail}",
        "ocr_eta": "~{eta} left",
        "ocr_eta_calc": "estimating time…",
        "ocr_running": "Running OCR…",
        "ocr_stopping": "Stopping…",
        "snip_ocr_running": "Screenshot OCR…",
        "ocr_stage_prepare": "Preparing image",
        "ocr_stage_pass": "Recognizing text ({current}/{total})",
        "ocr_stage_merge": "Finalizing text",
        "ocr_stage_done": "Finishing",
        "ocr_page_ready": "Page {page} ready",
        "saved_searchable_pdf": "Saved searchable PDF: {path}",
        "saved_text_pdf": "Saved text PDF: {path}",
        "settings": "OCR Settings",
        "ocr_lang": "OCR language",
        "ocr_mode": "Speed / accuracy",
        "mode_fast": "Fast (quicker, lighter)",
        "mode_accurate": "Accurate (better for small text)",
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
        "select_folder": "Process Folder",
        "batch_progress": "File {current} of {total}: {name}",
        "batch_done": "Batch OCR complete ({count} files, {elapsed:.1f}s)",
        "shortcuts": "Ctrl+O open · Ctrl+C copy · Ctrl+S save",
        "preview": "Document Preview",
        "actions": "Actions",
        "author_by": "By {name}",
        "author_link": "GitHub",
        "engine_loading": "Loading OCR models (first run may take a minute)...",
        "engine_ready": "OCR engine ready",
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
        "ocr_progress": "{percent}٪ انجام شده · {detail}",
        "ocr_eta": "حدود {eta} باقی‌مانده",
        "ocr_eta_calc": "در حال برآورد زمان…",
        "ocr_running": "در حال اجرای OCR…",
        "ocr_stopping": "در حال توقف…",
        "snip_ocr_running": "OCR تصویر صفحه‌نمایش…",
        "ocr_stage_prepare": "آماده‌سازی تصویر",
        "ocr_stage_pass": "تشخیص متن ({current}/{total})",
        "ocr_stage_merge": "نهایی‌سازی متن",
        "ocr_stage_done": "در حال اتمام",
        "ocr_page_ready": "صفحه {page} آماده شد",
        "saved_searchable_pdf": "PDF قابل جستجو ذخیره شد: {path}",
        "saved_text_pdf": "PDF متنی ذخیره شد: {path}",
        "settings": "تنظیمات OCR",
        "ocr_lang": "زبان OCR",
        "ocr_mode": "سرعت / دقت",
        "mode_fast": "سریع (سبک‌تر)",
        "mode_accurate": "دقیق (بهتر برای متن ریز)",
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
        "select_folder": "پردازش پوشه",
        "batch_progress": "فایل {current} از {total}: {name}",
        "batch_done": "OCR دسته‌ای کامل شد ({count} فایل، {elapsed:.1f} ثانیه)",
        "shortcuts": "Ctrl+O باز کردن · Ctrl+C کپی · Ctrl+S ذخیره",
        "preview": "پیش‌نمایش سند",
        "actions": "عملیات",
        "author_by": "توسط {name}",
        "author_link": "گیت‌هاب",
        "engine_loading": "در حال بارگذاری مدل‌های OCR (اولین اجرا ممکن است کمی طول بکشد)...",
        "engine_ready": "موتور OCR آماده است",
    },
}


def get_resource_dir():
    if getattr(sys, "frozen", False):
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
        self._ocr_start_time = 0.0
        self._ocr_progress_fraction = 0.0
        self._ocr_progress_detail = ""
        self._ocr_unit_base = 0.0
        self._ocr_unit_span = 1.0
        self._ocr_total_units = 1
        self._ocr_completed_units = 0
        self._ocr_unit_started_at = 0.0
        self._ocr_unit_durations = []
        self._progress_active = False
        self._progress_gen = 0
        self._snip_progress_active = False

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
        _settings = load_settings()
        snipping_tool.configure(
            lang=_settings.get("ocr_lang", "fas+eng"),
            mode=_settings.get("ocr_mode", "accurate"),
            on_start=lambda: [
                setattr(self.page.window, "minimized", True),
                self.page.update(),
            ],
            on_end=lambda: [
                setattr(self.page.window, "minimized", False),
                setattr(self.page.window, "focused", True),
                self.page.update(),
            ],
            on_text_extracted=self._on_text_extracted,
            on_ocr_progress=self._on_snip_ocr_progress,
            on_ocr_busy=self._on_snip_ocr_busy,
        )
        snipping_tool.start_hotkey_listener()
        self._apply_language()
        self._build_layout()
        self._enable_file_drop()
        threading.Thread(target=self._warm_ocr_engine, daemon=True).start()

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
        self.mode_dropdown = ft.Dropdown(
            options=[
                ft.DropdownOption(key="accurate", text=self.t("mode_accurate")),
                ft.DropdownOption(key="fast", text=self.t("mode_fast")),
            ],
            value="accurate",
            border_color=COLORS["card_border"],
            bgcolor=COLORS["input"],
            color=COLORS["text"],
            on_select=self._on_settings_changed,
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

        self.progress = ft.ProgressBar(
            value=0,
            visible=False,
            color=COLORS["primary"],
            bgcolor=COLORS["input"],
        )
        self.progress_percent = ft.Text("0%", size=13, weight=ft.FontWeight.W_600, color=COLORS["text"])
        self.progress_label = ft.Text("", size=12, color=COLORS["muted"], expand=True)
        self.progress_eta = ft.Text("", size=12, color=COLORS["info"])
        self.progress_panel = ft.Column(
            visible=False,
            spacing=8,
            controls=[
                ft.Row(
                    [
                        self.progress_percent,
                        self.progress_label,
                        self.progress_eta,
                    ],
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                self.progress,
            ],
        )
        self.result_stats = ft.Text("", size=12, color=COLORS["muted"])
        self.result_field = ft.TextField(
            multiline=True,
            min_lines=14,
            width=RESULT_WIDTH,
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
        mode = settings.get("ocr_mode", "accurate")
        self.mode_dropdown.value = mode if mode in ("fast", "accurate") else "accurate"
        self.export_dropdown.value = settings.get("export_format", "txt")

    def _persist_settings(self):
        save_settings({
            "ui_language": self.language,
            "ocr_lang": self.lang_dropdown.value,
            "ocr_mode": self.mode_dropdown.value,
            "export_format": self.export_dropdown.value,
        })

    def _on_settings_changed(self, _=None):
        self._persist_settings()
        snipping_tool.configure(
            lang=self.lang_dropdown.value or "fas+eng",
            mode=self.mode_dropdown.value or "accurate",
            on_ocr_progress=self._on_snip_ocr_progress,
            on_ocr_busy=self._on_snip_ocr_busy,
        )

    def _warm_ocr_engine(self):
        try:
            self.page.run_task(self._log_engine, self.t("engine_loading"), "info")
        except Exception:
            pass
        try:
            warm_reader()
            self.page.run_task(self._log_engine, self.t("engine_ready"), "success")
        except Exception as exc:
            self.page.run_task(self._log_engine, str(exc), "error")

    async def _log_engine(self, message, level="info"):
        self._log(message, level)
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
                self._setting_block(self.t("ocr_mode"), self.mode_dropdown),
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
                    self.progress_panel,
                    ft.Row(
                        [self._setting_block(self.t("export_format"), self.export_dropdown), self.save_btn],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
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
        self.page.window.width = 1200
        self.page.window.height = 940
        self.page.window.min_width = 1000
        self.page.window.min_height = 760

        align = ft.TextAlign.RIGHT if self.language == "fa" else ft.TextAlign.LEFT
        self.result_field.text_align = align
        self.result_field.width = RESULT_WIDTH

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
        self.mode_dropdown.label = self.t("ocr_mode")
        self.mode_dropdown.options = [
            ft.DropdownOption(key="accurate", text=self.t("mode_accurate")),
            ft.DropdownOption(key="fast", text=self.t("mode_fast")),
        ]
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
        self.shortcuts_hint.value = (
            f"{self.t('shortcuts')}  ·  "
            "Win+Shift+D: Screen snip & type"
            if self.language == "en" else
            f"{self.t('shortcuts')}  ·  "
            "Win+Shift+D: برش صفحه و تایپ زنده"
        )
        self.result_field.hint_text = self.t("result_empty")
        self._update_result_stats()
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

        self._render_preview()
        self.run_btn.disabled = False
        self.save_btn.disabled = True
        self.copy_btn.disabled = True
        self.clear_btn.disabled = True
        self.result_field.value = ""
        self._update_result_stats()
        self.progress.visible = False
        self.progress_panel.visible = False
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

    def _render_preview(self):
        if not self.file_path:
            return
        try:
            image = self._get_source_image(for_preview=True)
            if not image:
                raise ValueError("no image")
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
            self._render_preview()
            self.page.update()

    def _next_preview_page(self, _):
        if self.preview_page < self.pdf_page_count:
            self.preview_page += 1
            self._update_preview_nav()
            self._render_preview()
            self.page.update()

    def _on_text_extracted(self, text, lang):
        self.result_field.value = text
        self.result_field.rtl = lang in ("fas", "fa")
        self.result_field.text_align = (
            ft.TextAlign.RIGHT if lang in ("fas", "fa", "fas+eng") else ft.TextAlign.LEFT
        )
        self.result_field.update()
        self._update_result_stats()
        self.save_btn.disabled = not bool(text.strip())
        self.copy_btn.disabled = not bool(text.strip())
        self.clear_btn.disabled = not bool(text.strip())
        snack = ft.SnackBar(content=ft.Text("✨ OCR complete! Text typed and loaded into the app."))
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()

    def _on_snip_ocr_busy(self, busy):
        try:
            self.page.run_task(self._snip_ocr_busy_async, bool(busy))
        except Exception:
            pass

    def _on_snip_ocr_progress(self, fraction, detail):
        if not self._snip_progress_active and not self._progress_active:
            return
        try:
            self.page.run_task(
                self._update_progress_async,
                float(fraction),
                detail or self.t("snip_ocr_running"),
                self._progress_gen,
            )
        except Exception:
            pass

    async def _snip_ocr_busy_async(self, busy):
        if busy:
            self._snip_progress_active = True
            self._progress_active = True
            self._progress_gen += 1
            self._ocr_start_time = time.time()
            self._ocr_mode = self.mode_dropdown.value or "accurate"
            self._ocr_progress_fraction = 0.0
            self._ocr_progress_detail = self.t("snip_ocr_running")
            self._apply_progress_ui(0.0, self.t("snip_ocr_running"), force=True)
            self.status_text.value = self.t("snip_ocr_running")
            self.stop_btn.disabled = True
            self._log(self.t("snip_ocr_running"), "info")
        else:
            self._snip_progress_active = False
            self._hide_progress_ui()
            if not self.ocr_running:
                self.stop_btn.disabled = True
                self.run_btn.disabled = False
        self.page.update()

    def _hide_progress_ui(self):
        """Clear progress bar and ignore any late progress callbacks."""
        self._progress_active = False
        self._snip_progress_active = False
        self._progress_gen += 1
        self.progress_panel.visible = False
        self.progress.visible = False
        self.progress.value = 0
        self.progress_label.value = ""
        self.progress_eta.value = ""
        self.progress_percent.value = "0%"
        self._ocr_progress_fraction = 0.0
        self._ocr_progress_detail = ""

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

    def _format_duration(self, seconds):
        if seconds is None or seconds < 0 or seconds == float("inf"):
            return "—"
        total = int(round(seconds))
        if total < 60:
            return f"{total}s" if self.language == "en" else f"{total} ثانیه"
        minutes, secs = divmod(total, 60)
        if minutes < 60:
            return f"{minutes}:{secs:02d}"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}:{minutes:02d}:{secs:02d}"

    def _stage_label(self, stage):
        stage = (stage or "").strip().lower()
        if stage.startswith("prepare"):
            return self.t("ocr_stage_prepare")
        if stage.startswith("pass"):
            # "pass 1/2"
            parts = stage.replace("pass", "").strip().split("/")
            try:
                current, total = int(parts[0]), int(parts[1])
            except (ValueError, IndexError):
                current, total = 1, 1
            return self.t("ocr_stage_pass").format(current=current, total=total)
        if stage.startswith("merge"):
            return self.t("ocr_stage_merge")
        if stage.startswith("done"):
            return self.t("ocr_stage_merge")
        return stage or self.t("ocr_running")

    def _estimate_eta_seconds(self, fraction):
        elapsed = time.time() - self._ocr_start_time if self._ocr_start_time else 0.0
        if fraction >= 0.999:
            return 0.0
        # Prefer average completed-unit timing when available
        if self._ocr_unit_durations and self._ocr_total_units > self._ocr_completed_units:
            avg = sum(self._ocr_unit_durations) / len(self._ocr_unit_durations)
            remaining_units = self._ocr_total_units - self._ocr_completed_units
            local = 0.0
            if self._ocr_unit_span > 0:
                local = max(0.0, min(1.0, (fraction - self._ocr_unit_base) / self._ocr_unit_span))
            current_left = max(0.0, 1.0 - local) * avg
            return current_left + max(0, remaining_units - 1) * avg
        # Early in a job: soft prior by mode so ETA doesn't explode while a pass is stuck
        prior = 20.0 if getattr(self, "_ocr_mode", "accurate") == "fast" else 35.0
        if fraction <= 0.12:
            return max(5.0, prior - elapsed)
        if fraction > 0.05 and elapsed > 0.5:
            return max(0.0, elapsed * (1.0 - fraction) / fraction)
        return None

    def _apply_progress_ui(self, fraction, detail="", force=False):
        if not force and not self._progress_active and not self.ocr_running:
            return
        fraction = max(0.0, min(1.0, float(fraction)))
        self._ocr_progress_fraction = fraction
        if detail:
            self._ocr_progress_detail = detail
        percent = int(round(fraction * 100))
        self.progress.visible = True
        self.progress_panel.visible = True
        self.progress.value = fraction
        self.progress_percent.value = f"{percent}%"
        detail_text = self._ocr_progress_detail or self.t("ocr_running")
        self.progress_label.value = self.t("ocr_progress").format(
            percent=percent, detail=detail_text,
        )
        eta = self._estimate_eta_seconds(fraction)
        if fraction >= 0.999:
            self.progress_eta.value = self.t("ocr_eta").format(eta=self._format_duration(0))
        elif eta is None:
            self.progress_eta.value = self.t("ocr_eta_calc")
        else:
            self.progress_eta.value = self.t("ocr_eta").format(eta=self._format_duration(eta))
        if self.ocr_running or self._snip_progress_active:
            self.status_text.value = (
                self.t("snip_ocr_running") if self._snip_progress_active and not self.ocr_running
                else self.t("ocr_running")
            )

    def _report_job_progress(self, fraction, stage=""):
        """Thread-safe progress from OCR worker (absolute 0..1 for whole job)."""
        if not self.ocr_running and not self._progress_active:
            return
        # Don't flash a lingering "Finishing" state from done callbacks
        if stage and stage.strip().lower().startswith("done"):
            detail = self._ocr_progress_detail or self.t("ocr_stage_merge")
        elif stage:
            detail = self._stage_label(stage)
        else:
            detail = self._ocr_progress_detail or self.t("ocr_running")
        gen = self._progress_gen
        self.page.run_task(self._update_progress_async, fraction, detail, gen)

    def _begin_unit(self, unit_index, total_units, detail):
        self._ocr_total_units = max(int(total_units), 1)
        self._ocr_completed_units = max(0, int(unit_index))
        self._ocr_unit_span = 1.0 / self._ocr_total_units
        self._ocr_unit_base = self._ocr_completed_units * self._ocr_unit_span
        self._ocr_unit_started_at = time.time()
        self._ocr_progress_detail = detail
        self._report_job_progress(self._ocr_unit_base)

    def _unit_progress_cb(self, local_fraction, stage=""):
        if not self.ocr_running and not self._progress_active:
            return
        overall = self._ocr_unit_base + self._ocr_unit_span * max(0.0, min(1.0, local_fraction))
        if stage and stage.strip().lower().startswith("done"):
            stage_detail = ""
        else:
            stage_detail = self._stage_label(stage) if stage else ""
        if self._ocr_progress_detail and stage_detail:
            detail = f"{self._ocr_progress_detail} — {stage_detail}"
        else:
            detail = stage_detail or self._ocr_progress_detail or self.t("ocr_running")
        gen = self._progress_gen
        self.page.run_task(self._update_progress_async, overall, detail, gen)

    def _finish_unit(self):
        if self._ocr_unit_started_at:
            self._ocr_unit_durations.append(max(0.05, time.time() - self._ocr_unit_started_at))
            if len(self._ocr_unit_durations) > 12:
                self._ocr_unit_durations = self._ocr_unit_durations[-12:]
        self._ocr_completed_units = min(self._ocr_total_units, self._ocr_completed_units + 1)
        # Progress only — avoid a "done/finishing" label that can linger
        self._report_job_progress(self._ocr_completed_units / self._ocr_total_units)

    def _get_options(self):
        return {
            "lang": self.lang_dropdown.value,
            "mode": self.mode_dropdown.value or "accurate",
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
        self._progress_active = True
        self._progress_gen += 1
        self._ocr_start_time = time.time()
        self._ocr_progress_fraction = 0.0
        self._ocr_progress_detail = self.t("ocr_running")
        self._ocr_mode = options.get("mode") or "accurate"
        self._ocr_unit_base = 0.0
        self._ocr_unit_span = 1.0
        self._ocr_total_units = 1
        self._ocr_completed_units = 0
        self._ocr_unit_started_at = 0.0
        self._ocr_unit_durations = []

        self.run_btn.disabled = True
        self.stop_btn.disabled = False
        self.save_btn.disabled = True
        self.copy_btn.disabled = True
        self.clear_btn.disabled = True
        self.result_field.value = ""
        self._update_result_stats()
        self._apply_progress_ui(0.0, self.t("ocr_running"), force=True)
        self._log("شروع OCR ..." if self.language == "fa" else "Starting OCR...", "info")
        self.page.update()

        threading.Thread(target=self._ocr_worker, args=(options,), daemon=True).start()
        threading.Thread(target=self._ocr_progress_heartbeat, daemon=True).start()

    def _ocr_progress_heartbeat(self):
        """Refresh percent/ETA UI while a long OCR pass is blocking."""
        gen = self._progress_gen
        while self.ocr_running and self._progress_gen == gen:
            time.sleep(1.0)
            if not self.ocr_running or self._progress_gen != gen:
                break
            try:
                detail = (
                    self.t("ocr_stopping")
                    if self.cancel_event.is_set()
                    else (self._ocr_progress_detail or self.t("ocr_running"))
                )
                self.page.run_task(
                    self._update_progress_async,
                    self._ocr_progress_fraction,
                    detail,
                    gen,
                )
            except Exception:
                break

    def _ocr_single_file(self, file_path, options, unit_index=0, total_units=1, detail=None, stream=False):
        ext = os.path.splitext(file_path)[1].lower()
        parts = []
        label = detail or os.path.basename(file_path)
        ocr_dpi = 200

        if ext == ".pdf":
            images = pdf_to_images(
                file_path, dpi=ocr_dpi,
                first_page=options["page_from"], last_page=options["page_to"],
            )
            page_total = max(len(images), 1)
            for i, img in enumerate(images):
                if self.cancel_event.is_set():
                    break
                page_num = options["page_from"] + i
                page_base = unit_index / max(total_units, 1)
                page_span = (1.0 / max(total_units, 1)) / page_total
                self._ocr_unit_base = page_base + i * page_span
                self._ocr_unit_span = page_span
                self._ocr_unit_started_at = time.time()
                self._ocr_progress_detail = self.t("ocr_page_progress").format(
                    current=page_num, total=options["page_from"] + page_total - 1,
                )
                text = run_ocr(
                    img,
                    lang=options["lang"],
                    mode=options["mode"],
                    progress_cb=self._unit_progress_cb,
                    cancel_check=self.cancel_event.is_set,
                )
                chunk = f"\n{self.t('result_page').format(page=page_num)}\n{text}"
                parts.append(chunk)
                if stream:
                    self.page.run_task(self._append_ocr_result, chunk, page_num)
                if self._ocr_unit_started_at:
                    self._ocr_unit_durations.append(max(0.05, time.time() - self._ocr_unit_started_at))
        else:
            self._begin_unit(unit_index, total_units, label)
            with Image.open(file_path) as img:
                text = run_ocr(
                    img,
                    lang=options["lang"],
                    mode=options["mode"],
                    progress_cb=self._unit_progress_cb,
                    cancel_check=self.cancel_event.is_set,
                )
                parts.append(text)
                if stream:
                    self.page.run_task(self._append_ocr_result, text, None)
            self._finish_unit()
        return "\n".join(parts)

    def _ocr_worker(self, options):
        try:
            start = time.time()
            batch_files = options.get("batch_files") or []

            if batch_files:
                all_text = []
                total = len(batch_files)
                self._ocr_total_units = total
                try:
                    for idx, file_path in enumerate(batch_files):
                        if self.cancel_event.is_set():
                            break
                        name = os.path.basename(file_path)
                        detail = self.t("batch_progress").format(
                            current=idx + 1, total=total, name=name,
                        )
                        header = f"\n=== {name} ===\n"
                        self.page.run_task(self._append_ocr_result, header, None)
                        file_text = self._ocr_single_file(
                            file_path, options, unit_index=idx, total_units=total,
                            detail=detail, stream=True,
                        )
                        all_text.append(header + file_text)
                except OCRCancelled:
                    pass
                result = "\n".join(all_text)
                elapsed = time.time() - start
                self.page.run_task(
                    self._finish_ocr, result, True if self.cancel_event.is_set() else False,
                    elapsed, total, True,
                )
                return

            ext = os.path.splitext(self.file_path)[1].lower()
            all_text = []
            streamed = False
            cancelled = False

            try:
                if ext == ".pdf":
                    images = pdf_to_images(
                        self.file_path, dpi=200,
                        first_page=options["page_from"], last_page=options["page_to"],
                    )
                    total = max(len(images), 1)
                    self._ocr_total_units = total
                    streamed = True
                    for i, img in enumerate(images):
                        if self.cancel_event.is_set():
                            cancelled = True
                            break
                        page_num = options["page_from"] + i
                        detail = self.t("ocr_page_progress").format(
                            current=page_num, total=options["page_from"] + total - 1,
                        )
                        self._begin_unit(i, total, detail)
                        text = run_ocr(
                            img,
                            lang=options["lang"],
                            mode=options["mode"],
                            progress_cb=self._unit_progress_cb,
                            cancel_check=self.cancel_event.is_set,
                        )
                        chunk = f"\n{self.t('result_page').format(page=page_num)}\n{text}"
                        all_text.append(chunk)
                        self.page.run_task(self._append_ocr_result, chunk, page_num)
                        self._finish_unit()
                    result = "\n".join(all_text)
                else:
                    if self.cancel_event.is_set():
                        self.page.run_task(self._finish_ocr, "", True, time.time() - start)
                        return
                    self._begin_unit(0, 1, self.t("ocr_running"))
                    with Image.open(self.file_path) as img:
                        result = run_ocr(
                            img,
                            lang=options["lang"],
                            mode=options["mode"],
                            progress_cb=self._unit_progress_cb,
                            cancel_check=self.cancel_event.is_set,
                        )
                    self._finish_unit()
            except OCRCancelled:
                cancelled = True
                result = "\n".join(all_text) if all_text else (self.result_field.value or "")

            elapsed = time.time() - start
            self.page.run_task(
                self._finish_ocr,
                result if not streamed else "\n".join(all_text),
                cancelled or self.cancel_event.is_set(),
                elapsed,
                0,
                streamed,
            )
        except OCRCancelled:
            self.page.run_task(
                self._finish_ocr,
                self.result_field.value or "",
                True,
                0,
                0,
                True,
            )
        except Exception as exc:
            self.page.run_task(self._ocr_failed, str(exc))
    async def _append_ocr_result(self, chunk, page_num=None):
        """Show page/file text in the result box as soon as it is ready."""
        existing = self.result_field.value or ""
        if existing and not existing.endswith("\n") and not chunk.startswith("\n"):
            existing += "\n"
        self.result_field.value = existing + chunk
        has_text = bool(self.result_field.value.strip())
        self.save_btn.disabled = not has_text
        self.copy_btn.disabled = not has_text
        self.clear_btn.disabled = not has_text
        self._update_result_stats()
        if page_num is not None:
            self._log(self.t("ocr_page_ready").format(page=page_num), "success")
        self.page.update()

    async def _update_progress_async(self, value, detail="", gen=None):
        if gen is not None and gen != self._progress_gen:
            return
        if not self._progress_active and not self.ocr_running:
            return
        self._apply_progress_ui(value, detail)
        self.page.update()

    async def _finish_ocr(self, text, cancelled, elapsed, batch_count=0, already_streamed=False):
        self.ocr_running = False
        self._hide_progress_ui()
        self.run_btn.disabled = False
        self.stop_btn.disabled = True

        if cancelled:
            if not already_streamed and text.strip():
                self.result_field.value = text
            if self.result_field.value.strip():
                self.status_text.value = "OCR متوقف شد. نتیجه جزئی حفظ شد." if self.language == "fa" else "OCR cancelled. Partial result kept."
                self._log(f"OCR متوقف شد ({elapsed:.1f}s)" if self.language == "fa" else f"OCR cancelled ({elapsed:.1f}s)", "info")
                self.save_btn.disabled = False
            else:
                self.status_text.value = "OCR متوقف شد." if self.language == "fa" else "OCR cancelled."
                self._log("OCR متوقف شد." if self.language == "fa" else "OCR cancelled.", "info")
        else:
            if not already_streamed:
                self.result_field.value = text
            self.status_text.value = "OCR با موفقیت انجام شد." if self.language == "fa" else "OCR complete."
            if batch_count:
                self._log(self.t("batch_done").format(count=batch_count, elapsed=elapsed), "success")
            else:
                self._log(f"OCR کامل شد ({elapsed:.1f}s)" if self.language == "fa" else f"OCR complete ({elapsed:.1f}s)", "success")
            self.save_btn.disabled = not bool(self.result_field.value.strip())

        has_text = bool(self.result_field.value.strip())
        self.copy_btn.disabled = not has_text
        self.clear_btn.disabled = not has_text
        self.stop_btn.disabled = True
        self.run_btn.disabled = False
        self._update_result_stats()
        self.page.update()

    async def _ocr_failed(self, message):
        self.ocr_running = False
        self._hide_progress_ui()
        self.run_btn.disabled = False
        self.stop_btn.disabled = True
        self.status_text.value = "خطا در اجرای OCR." if self.language == "fa" else "OCR failed."
        self._log(f"OCR failed: {message}", "error")
        self.page.update()

    def _stop_ocr(self, _):
        if not self.ocr_running:
            return
        self.cancel_event.set()
        self.stop_btn.disabled = True
        self.status_text.value = self.t("ocr_stopping")
        self.progress_eta.value = self.t("ocr_stopping")
        self.progress_label.value = self.t("ocr_progress").format(
            percent=int(round(self._ocr_progress_fraction * 100)),
            detail=self.t("ocr_stopping"),
        )
        self._log(self.t("ocr_stopping"), "info")
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
            result_kind = save_export(
                path,
                self.result_field.value,
                export_fmt,
            )
            if result_kind == "pdf_text":
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
