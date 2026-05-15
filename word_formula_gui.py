from __future__ import annotations

import shutil
import tempfile
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk

from formula_docx import SUPPORTED_FORMULA_FONTS, build_docx, find_mml2omml_path, parse_equations
from formula_preview import build_preview_items
from formula_symbols import SYMBOL_GROUPS, preferred_cursor_offset
from platform_utils import open_path
from ui_branding import (
    APP_BACKGROUND,
    APP_ICON_ICO,
    APP_ICON_PNG,
    APP_TITLE,
    BOTTOM_WATERMARK_COLOR,
    BOTTOM_WATERMARK_FONT_SIZE,
    BOTTOM_WATERMARK_STEP_X,
    BOTTOM_WATERMARK_STEP_Y,
    FROSTED_PANEL_BACKGROUND,
    HELP_TEXT,
    TRANSLUCENT_EDITOR_BACKGROUND,
    WATERMARK_TEXT,
)


class ToolTip:
    def __init__(self, widget: tk.Widget, text: str) -> None:
        self.widget = widget
        self.text = text
        self.window: tk.Toplevel | None = None
        widget.bind("<Enter>", self._show)
        widget.bind("<Leave>", self._hide)
        widget.bind("<ButtonPress>", self._hide)

    def _show(self, event: tk.Event | None = None) -> None:
        if self.window is not None or not self.text:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 8
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        self.window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            self.window,
            text=self.text,
            justify="left",
            background="#111827",
            foreground="#ffffff",
            borderwidth=0,
            padx=8,
            pady=5,
            font=("Segoe UI", 9),
        )
        label.pack()

    def _hide(self, event: tk.Event | None = None) -> None:
        if self.window is not None:
            self.window.destroy()
            self.window = None


class WatermarkFrame(tk.Frame):
    def __init__(self, master: tk.Misc, background: str = APP_BACKGROUND, **kwargs) -> None:
        super().__init__(master, bg=background, **kwargs)
        self.canvas = tk.Canvas(self, bg=background, highlightthickness=0, borderwidth=0)
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.canvas.tk.call("lower", self.canvas._w)


class BottomWatermarkStrip(tk.Frame):
    def __init__(self, master: tk.Misc, **kwargs) -> None:
        super().__init__(master, bg=APP_BACKGROUND, **kwargs)
        self.font_size = BOTTOM_WATERMARK_FONT_SIZE
        self.step_x = BOTTOM_WATERMARK_STEP_X
        self.step_y = BOTTOM_WATERMARK_STEP_Y
        self.offset_y = 0
        self.animation_job: str | None = None
        self.canvas = tk.Canvas(self, bg=APP_BACKGROUND, highlightthickness=0, borderwidth=0, height=36)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", self._redraw)
        self.canvas.bind("<Configure>", self._redraw)
        self._start_animation()

    def _redraw(self, event: tk.Event | None = None) -> None:
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self.canvas.delete("bottom-watermark")
        for y in range(-self.step_y, height + self.step_y * 2, self.step_y):
            row_y = y + self.offset_y
            for x in range(-self.step_x, width + self.step_x * 2, self.step_x):
                self.canvas.create_text(
                    x,
                    row_y,
                    text=WATERMARK_TEXT,
                    angle=0,
                    anchor="w",
                    fill=BOTTOM_WATERMARK_COLOR,
                    font=("Segoe UI", self.font_size),
                    tags="bottom-watermark",
                )

    def _start_animation(self) -> None:
        if self.winfo_exists() and self.animation_job is None:
            self.animation_job = self.after(80, self._animate)

    def _animate(self) -> None:
        self.animation_job = None
        if not self.winfo_exists():
            return
        self.offset_y = (self.offset_y + 1) % self.step_y
        self._redraw()
        self._start_animation()

    def stop_animation(self) -> None:
        if self.animation_job is not None:
            try:
                self.after_cancel(self.animation_job)
            except tk.TclError:
                pass
            self.animation_job = None


class WordFormulaStudio(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1260x780")
        self.minsize(1080, 680)
        self.configure(bg=APP_BACKGROUND)

        self.output_path = tk.StringVar(value=str(Path.cwd() / "word-native-formulas.docx"))
        self.open_after_generate = tk.BooleanVar(value=True)
        self.formula_font = tk.StringVar(value="Cambria Math")
        self.preview_job: str | None = None
        self.preview_dir = Path(tempfile.mkdtemp(prefix="word-formula-preview-"))
        self.preview_images: list[ImageTk.PhotoImage] = []
        self.app_icon: ImageTk.PhotoImage | None = None
        self.bottom_watermark: BottomWatermarkStrip | None = None
        self.is_startup_maximized = False

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._set_app_icon()
        self._build_style()
        self._build_ui()
        self._bind_shortcuts()
        self._check_word_support()
        self._schedule_preview()
        self._maximize_on_start()

    def _set_app_icon(self) -> None:
        try:
            if APP_ICON_ICO.exists():
                self.iconbitmap(str(APP_ICON_ICO))
            if APP_ICON_PNG.exists():
                self.app_icon = ImageTk.PhotoImage(Image.open(APP_ICON_PNG))
                self.iconphoto(True, self.app_icon)
        except Exception:
            pass

    def _maximize_on_start(self) -> None:
        try:
            self.state("zoomed")
            self.is_startup_maximized = True
            return
        except tk.TclError:
            pass

        try:
            self.attributes("-zoomed", True)
            self.is_startup_maximized = True
        except tk.TclError:
            self.is_startup_maximized = False

    def _build_style(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("App.TFrame", background=FROSTED_PANEL_BACKGROUND)
        style.configure("Plain.TFrame", background=APP_BACKGROUND)
        style.configure("Toolbar.TFrame", background=FROSTED_PANEL_BACKGROUND)
        style.configure("Status.TFrame", background=FROSTED_PANEL_BACKGROUND)
        style.configure("TLabel", background=FROSTED_PANEL_BACKGROUND, foreground="#172033", font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=FROSTED_PANEL_BACKGROUND, foreground="#111827", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", background=FROSTED_PANEL_BACKGROUND, foreground="#64748b", font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=FROSTED_PANEL_BACKGROUND, foreground="#111827", font=("Segoe UI", 12, "bold"))
        style.configure("Hint.TLabel", background=FROSTED_PANEL_BACKGROUND, foreground="#64748b", font=("Segoe UI", 9))
        style.configure("Status.TLabel", background=FROSTED_PANEL_BACKGROUND, foreground="#64748b", font=("Segoe UI", 9))

        style.configure(
            "TButton",
            background="#ffffff",
            bordercolor="#d6dde7",
            focusthickness=1,
            focuscolor="#8fb7ff",
            font=("Segoe UI", 10),
            padding=(12, 8),
            relief="flat",
        )
        style.map(
            "TButton",
            background=[("active", "#f3f7ff"), ("pressed", "#e8f0ff")],
            bordercolor=[("active", "#9bbcf4"), ("pressed", "#7fa7e8")],
        )
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=(15, 9))
        style.configure("Symbol.TButton", font=("Segoe UI", 10), padding=(10, 7))
        style.configure("TCheckbutton", background="#ffffff", foreground="#172033", font=("Segoe UI", 10))
        style.map("TCheckbutton", background=[("active", "#ffffff")])
        style.configure("TEntry", fieldbackground="#ffffff", padding=(8, 6))
        style.configure("TCombobox", fieldbackground="#ffffff", padding=(8, 6))
        style.configure("TPanedwindow", background="#ffffff")
        style.configure("TNotebook", background="#ffffff", borderwidth=0)
        style.configure("TNotebook.Tab", background="#ffffff", padding=(14, 7), font=("Segoe UI", 10))
        style.map("TNotebook.Tab", background=[("selected", "#f5f8fc"), ("active", "#f8fbff")])

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        self._build_header()
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=1, column=0, sticky="ew")
        self._build_main_area()
        ttk.Separator(self, orient=tk.HORIZONTAL).grid(row=3, column=0, sticky="ew")
        self._build_status_bar()
        self._build_bottom_watermark()

    def _build_header(self) -> None:
        header = WatermarkFrame(self, background=FROSTED_PANEL_BACKGROUND)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        header.grid_propagate(False)
        header.configure(height=92)

        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").grid(row=0, column=0, sticky="w", padx=(24, 0), pady=(18, 0))
        ttk.Label(
            header,
            text="把 LaTeX 转成 Word 原生矢量公式，支持预览、字体选择和符号快捷插入。",
            style="Subtitle.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=(24, 0), pady=(4, 0))

        tools = ttk.Frame(header, style="Toolbar.TFrame")
        tools.grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, 24), pady=(18, 0))
        ttk.Label(tools, text="Word 公式字体").grid(row=0, column=0, sticky="e", padx=(0, 8))
        self.font_combo = ttk.Combobox(
            tools,
            textvariable=self.formula_font,
            values=SUPPORTED_FORMULA_FONTS,
            state="readonly",
            width=22,
        )
        self.font_combo.grid(row=0, column=1, sticky="e", padx=(0, 10))
        self.font_combo.bind("<<ComboboxSelected>>", self._on_font_changed)
        ttk.Button(tools, text="刷新预览", command=self._refresh_preview).grid(row=0, column=2, padx=(0, 8))
        ttk.Button(tools, text="复制 LaTeX", command=self._copy_latex_source).grid(row=0, column=3, padx=(0, 8))
        ttk.Button(tools, text="生成 Word", style="Accent.TButton", command=self._generate).grid(
            row=0, column=4, padx=(0, 8)
        )
        help_button = ttk.Button(tools, text="?", width=3, command=self._show_help)
        help_button.grid(row=0, column=5)
        ToolTip(help_button, "使用说明")

    def _build_main_area(self) -> None:
        main = WatermarkFrame(self, background=APP_BACKGROUND)
        main.grid(row=2, column=0, sticky="nsew")
        main.columnconfigure(0, weight=1)
        main.rowconfigure(0, weight=1)

        paned = ttk.PanedWindow(main, orient=tk.HORIZONTAL)
        paned.grid(row=0, column=0, sticky="nsew", padx=24, pady=(14, 0))

        input_panel = WatermarkFrame(paned, background=FROSTED_PANEL_BACKGROUND)
        preview_panel = WatermarkFrame(paned, background=FROSTED_PANEL_BACKGROUND)
        self.input_panel = input_panel
        self.preview_panel = preview_panel
        paned.add(input_panel, weight=5)
        paned.add(preview_panel, weight=7)

        self._build_input_panel(input_panel)
        self._build_preview_panel(preview_panel)

        output = WatermarkFrame(main, background=FROSTED_PANEL_BACKGROUND)
        output.grid(row=1, column=0, sticky="ew", padx=24, pady=(14, 12))
        output.columnconfigure(1, weight=1)
        ttk.Label(output, text="输出文件").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(output, textvariable=self.output_path, font=("Segoe UI", 10)).grid(row=0, column=1, sticky="ew")
        ttk.Button(output, text="选择", command=self._choose_output).grid(row=0, column=2, padx=(10, 0))
        ttk.Button(output, text="打开文件夹", command=self._open_output_folder).grid(row=0, column=3, padx=(8, 0))
        ttk.Checkbutton(output, text="生成后打开 Word", variable=self.open_after_generate).grid(
            row=0, column=4, padx=(12, 0)
        )

    def _build_status_bar(self) -> None:
        footer = WatermarkFrame(self, background=FROSTED_PANEL_BACKGROUND)
        footer.grid(row=4, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        footer.grid_propagate(False)
        footer.configure(height=42)

        self.status_label = ttk.Label(footer, text="就绪", style="Status.TLabel")
        self.status_label.grid(row=0, column=0, sticky="w", padx=(24, 0), pady=9)
        ttk.Label(
            footer,
            text="Ctrl+Enter 生成 Word  ·  Ctrl+R 刷新预览  ·  Ctrl+Shift+C 复制 LaTeX",
            style="Status.TLabel",
        ).grid(row=0, column=1, sticky="e", padx=(0, 24), pady=9)

    def _build_bottom_watermark(self) -> None:
        self.bottom_watermark = BottomWatermarkStrip(self)
        self.bottom_watermark.grid(row=5, column=0, sticky="ew")

    def _build_input_panel(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(6, weight=1)

        ttk.Label(parent, text="编辑内容", style="Section.TLabel").grid(row=0, column=0, sticky="w")

        ttk.Label(parent, text="文档标题").grid(row=1, column=0, sticky="w", pady=(12, 0))
        self.title_entry = ttk.Entry(parent, font=("Segoe UI", 11))
        self.title_entry.insert(0, "Word 原生矢量公式")
        self.title_entry.grid(row=2, column=0, sticky="ew", pady=(6, 10))

        ttk.Label(parent, text="正文说明").grid(row=3, column=0, sticky="w")
        self.intro_text = tk.Text(
            parent,
            height=3,
            wrap="word",
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d8dee8",
            highlightcolor="#7aa7ff",
            padx=10,
            pady=8,
            bg=TRANSLUCENT_EDITOR_BACKGROUND,
            fg="#172033",
            insertbackground="#172033",
        )
        self.intro_text.insert("1.0", "以下公式由 LaTeX 转换为 Word 原生公式对象。")
        self.intro_text.grid(row=4, column=0, sticky="ew", pady=(6, 12))

        formula_header = ttk.Frame(parent, style="App.TFrame")
        formula_header.grid(row=5, column=0, sticky="ew")
        formula_header.columnconfigure(0, weight=1)
        ttk.Label(formula_header, text="LaTeX 公式（每行一个）").grid(row=0, column=0, sticky="w")
        ttk.Label(formula_header, text="输入会自动刷新右侧预览", style="Hint.TLabel").grid(row=0, column=1, sticky="e")

        text_frame = ttk.Frame(parent, style="App.TFrame")
        text_frame.grid(row=6, column=0, sticky="nsew", pady=(6, 10))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.equation_text = tk.Text(
            text_frame,
            wrap="none",
            font=("Cascadia Mono", 11),
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d8dee8",
            highlightcolor="#7aa7ff",
            padx=10,
            pady=8,
            undo=True,
            bg=TRANSLUCENT_EDITOR_BACKGROUND,
            fg="#111827",
            insertbackground="#111827",
        )
        y_scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.equation_text.yview)
        x_scroll = ttk.Scrollbar(text_frame, orient="horizontal", command=self.equation_text.xview)
        self.equation_text.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.equation_text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        self.equation_text.insert(
            "1.0",
            "\\frac{d}{dx}\\left(\\int_{0}^{x} f(t)\\,dt\\right)=f(x)\n"
            "E = mc^2\n"
            "\\int_{0}^{\\infty} e^{-x^2}\\,dx = \\frac{\\sqrt{\\pi}}{2}",
        )
        self.equation_text.bind("<<Modified>>", self._on_equations_modified)

        self._build_symbol_palette(parent)

    def _build_symbol_palette(self, parent: ttk.Frame) -> None:
        ttk.Label(parent, text="符号库", style="Section.TLabel").grid(row=7, column=0, sticky="w", pady=(2, 6))
        notebook = ttk.Notebook(parent)
        notebook.grid(row=8, column=0, sticky="ew")

        for group in SYMBOL_GROUPS:
            page = ttk.Frame(notebook, style="App.TFrame", padding=(8, 10, 8, 4))
            notebook.add(page, text=group.name)
            columns = 4
            for column in range(columns):
                page.columnconfigure(column, weight=1, uniform=f"{group.name}-symbols")

            for index, symbol in enumerate(group.symbols):
                button = ttk.Button(
                    page,
                    text=symbol.display,
                    style="Symbol.TButton",
                    command=lambda snippet=symbol.snippet: self.insert_latex_snippet(snippet),
                )
                tooltip_text = symbol.hint or symbol.snippet
                ToolTip(button, f"{tooltip_text}\n{symbol.snippet}")
                button.grid(
                    row=index // columns,
                    column=index % columns,
                    sticky="ew",
                    padx=(0 if index % columns == 0 else 6, 0),
                    pady=(0, 6),
                )

    def _build_preview_panel(self, parent: ttk.Frame) -> None:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)

        top = ttk.Frame(parent, style="App.TFrame")
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        ttk.Label(top, text="实时预览", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        self.preview_count_label = ttk.Label(top, text="0 个公式", style="Hint.TLabel")
        self.preview_count_label.grid(row=0, column=1, sticky="e")

        canvas_frame = ttk.Frame(parent, style="App.TFrame")
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        self.preview_canvas = tk.Canvas(
            canvas_frame,
            bg=TRANSLUCENT_EDITOR_BACKGROUND,
            highlightthickness=1,
            highlightbackground="#d8dee8",
        )
        self.preview_inner = ttk.Frame(self.preview_canvas, style="App.TFrame", padding=(12, 10))
        y_scroll = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.preview_canvas.yview)
        self.preview_canvas.configure(yscrollcommand=y_scroll.set)
        self.preview_window = self.preview_canvas.create_window((0, 0), window=self.preview_inner, anchor="nw")

        self.preview_canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        self.preview_inner.bind("<Configure>", self._sync_preview_scrollregion)
        self.preview_canvas.bind("<Configure>", self._resize_preview_window)
        self.preview_canvas.bind_all("<MouseWheel>", self._on_preview_mousewheel)

    def _bind_shortcuts(self) -> None:
        self.bind_all("<Control-Return>", self._generate_from_shortcut)
        self.bind_all("<Control-r>", self._refresh_preview_from_shortcut)
        self.bind_all("<Control-R>", self._refresh_preview_from_shortcut)
        self.bind_all("<Control-Shift-C>", self._copy_latex_from_shortcut)

    def _on_equations_modified(self, event: tk.Event) -> None:
        if self.equation_text.edit_modified():
            self.equation_text.edit_modified(False)
            self._schedule_preview()

    def _schedule_preview(self) -> None:
        if self.preview_job is not None:
            self.after_cancel(self.preview_job)
        self.preview_job = self.after(350, self._refresh_preview)

    def _refresh_preview(self) -> None:
        self.preview_job = None
        equations = parse_equations(self.equation_text.get("1.0", "end"))
        shutil.rmtree(self.preview_dir, ignore_errors=True)
        self.preview_dir.mkdir(parents=True, exist_ok=True)
        self.preview_images.clear()

        for child in self.preview_inner.winfo_children():
            child.destroy()

        if not equations:
            ttk.Label(
                self.preview_inner,
                text="左侧输入 LaTeX 后，这里会显示预览。",
                style="Hint.TLabel",
            ).grid(row=0, column=0, sticky="w")
            self.preview_count_label.configure(text="0 个公式")
            return

        items = build_preview_items(equations, self.preview_dir, formula_font=self.formula_font.get())
        ok_count = sum(1 for item in items if item.ok)
        self.preview_count_label.configure(text=f"{ok_count}/{len(items)} 个可预览")

        wrap_length = max(420, self.preview_canvas.winfo_width() - 130)
        for row, item in enumerate(items):
            block = ttk.Frame(self.preview_inner, style="App.TFrame", padding=(0, 0, 0, 12))
            block.grid(row=row * 2, column=0, sticky="ew")
            block.columnconfigure(1, weight=1)

            ttk.Label(block, text=f"#{item.index}", style="Hint.TLabel").grid(
                row=0, column=0, sticky="nw", padx=(0, 12)
            )
            if item.ok and item.image_path:
                image = Image.open(item.image_path)
                max_width = max(360, self.preview_canvas.winfo_width() - 110)
                if image.width > max_width:
                    ratio = max_width / image.width
                    image = image.resize((int(image.width * ratio), int(image.height * ratio)))
                photo = ImageTk.PhotoImage(image)
                self.preview_images.append(photo)
                ttk.Label(block, image=photo, background="#ffffff").grid(row=0, column=1, sticky="w")
            else:
                ttk.Label(
                    block,
                    text=f"预览失败：{item.message}",
                    foreground="#c2413b",
                    background="#ffffff",
                    wraplength=wrap_length,
                ).grid(row=0, column=1, sticky="w")

            ttk.Label(block, text=item.latex, style="Hint.TLabel", wraplength=wrap_length).grid(
                row=1, column=1, sticky="ew", pady=(8, 0)
            )

            if row < len(items) - 1:
                ttk.Separator(self.preview_inner, orient=tk.HORIZONTAL).grid(
                    row=row * 2 + 1, column=0, sticky="ew", pady=(0, 12)
                )

        self._sync_preview_scrollregion()

    def _sync_preview_scrollregion(self, event: tk.Event | None = None) -> None:
        self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))

    def _resize_preview_window(self, event: tk.Event) -> None:
        self.preview_canvas.itemconfigure(self.preview_window, width=event.width)

    def _on_preview_mousewheel(self, event: tk.Event) -> None:
        if self.focus_get() and str(self.focus_get()).startswith(str(self.preview_canvas)):
            self.preview_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_font_changed(self, event: tk.Event | None = None) -> None:
        self._set_status(f"Word 公式字体已切换为：{self.formula_font.get()}", ok=True)
        self._schedule_preview()

    def _show_help(self) -> None:
        window = tk.Toplevel(self)
        window.title("使用说明")
        window.transient(self)
        window.resizable(False, False)
        window.configure(bg="#ffffff")
        try:
            if self.app_icon is not None:
                window.iconphoto(True, self.app_icon)
            elif APP_ICON_ICO.exists():
                window.iconbitmap(str(APP_ICON_ICO))
        except Exception:
            pass

        container = ttk.Frame(window, style="App.TFrame", padding=22)
        container.grid(row=0, column=0, sticky="nsew")
        ttk.Label(container, text="使用说明", style="Section.TLabel").grid(row=0, column=0, sticky="w")
        text = tk.Text(
            container,
            width=72,
            height=16,
            wrap="word",
            font=("Segoe UI", 10),
            relief="flat",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d8dee8",
            padx=12,
            pady=10,
            bg="#ffffff",
            fg="#172033",
        )
        text.grid(row=1, column=0, sticky="ew", pady=(12, 14))
        text.insert("1.0", HELP_TEXT)
        text.configure(state="disabled")
        ttk.Button(container, text="关闭", command=window.destroy).grid(row=2, column=0, sticky="e")
        window.update_idletasks()
        x = self.winfo_rootx() + max(40, (self.winfo_width() - window.winfo_width()) // 2)
        y = self.winfo_rooty() + max(40, (self.winfo_height() - window.winfo_height()) // 2)
        window.geometry(f"+{x}+{y}")
        window.grab_set()

    def insert_latex_snippet(self, snippet: str) -> None:
        try:
            start = self.equation_text.index("sel.first")
            end = self.equation_text.index("sel.last")
            self.equation_text.delete(start, end)
            insert_at = start
        except tk.TclError:
            insert_at = self.equation_text.index("insert")

        self.equation_text.insert(insert_at, snippet)
        cursor_offset = preferred_cursor_offset(snippet)
        self.equation_text.mark_set("insert", f"{insert_at}+{cursor_offset}c")
        self.equation_text.see("insert")
        self.equation_text.focus_set()
        self._schedule_preview()

    def _copy_latex_source(self) -> None:
        latex = "\n".join(parse_equations(self.equation_text.get("1.0", "end")))
        self.clipboard_clear()
        self.clipboard_append(latex)
        self._set_status("已复制左侧 LaTeX 源码", ok=True)

    def _copy_latex_from_shortcut(self, event: tk.Event) -> str:
        self._copy_latex_source()
        return "break"

    def _refresh_preview_from_shortcut(self, event: tk.Event) -> str:
        self._refresh_preview()
        return "break"

    def _generate_from_shortcut(self, event: tk.Event) -> str:
        self._generate()
        return "break"

    def _check_word_support(self) -> None:
        try:
            path = find_mml2omml_path()
            self._set_status(f"已检测到 Word 公式转换组件：{path}", ok=True)
        except Exception as exc:
            self._set_status(str(exc), ok=False)

    def _set_status(self, message: str, ok: bool = True) -> None:
        self.status_label.configure(text=message, foreground="#18875f" if ok else "#c2413b")

    def _choose_output(self) -> None:
        selected = filedialog.asksaveasfilename(
            title="保存 Word 文档",
            defaultextension=".docx",
            filetypes=[("Word 文档", "*.docx")],
            initialfile=Path(self.output_path.get()).name,
        )
        if selected:
            self.output_path.set(selected)

    def _open_output_folder(self) -> None:
        output = Path(self.output_path.get()).expanduser()
        folder = output.parent if output.parent.exists() else Path.cwd()
        open_path(folder)

    def _generate(self) -> None:
        try:
            equations = parse_equations(self.equation_text.get("1.0", "end"))
            output = build_docx(
                self.output_path.get(),
                title=self.title_entry.get(),
                intro=self.intro_text.get("1.0", "end"),
                equations=equations,
                formula_font=self.formula_font.get(),
            )
            self._set_status(f"已生成：{output}", ok=True)
            if self.open_after_generate.get():
                open_path(output)
        except Exception as exc:
            self._set_status(str(exc), ok=False)
            messagebox.showerror(APP_TITLE, str(exc))

    def _on_close(self) -> None:
        if self.bottom_watermark is not None:
            self.bottom_watermark.stop_animation()
        if self.preview_job is not None:
            try:
                self.after_cancel(self.preview_job)
            except tk.TclError:
                pass
            self.preview_job = None
        shutil.rmtree(self.preview_dir, ignore_errors=True)
        self.destroy()


def main() -> int:
    app = WordFormulaStudio()
    app.mainloop()
    return 0
