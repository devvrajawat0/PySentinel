"""
PySentinel — System Health Snapshot
app.py — Premium Graphical User Interface (v2.0)

Requires : Python 3.10+ with tkinter (built-in)
Run with : python app.py

Architecture:
  This file imports all monitoring logic from monitor.py.
  It never calculates disk stats itself — it only displays them.
  monitor.py remains fully functional without this file.

Author : You (SkillMe Python Internship — Week 1)
Version: 2.0.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
import sys
import datetime

# ── Import core monitoring logic from monitor.py ──────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import monitor


# ══════════════════════════════════════════════════════════════
# DESIGN SYSTEM
# All colors, fonts, and spacing live here — one source of truth.
# ══════════════════════════════════════════════════════════════

C = {
    # Backgrounds
    "white":        "#FFFFFF",
    "bg":           "#F7F8FA",
    "sidebar":      "#FFFFFF",
    "card":         "#FFFFFF",

    # Orange accent palette
    "accent":       "#F97316",
    "accent_dark":  "#EA6C10",
    "accent_light": "#FFF4ED",
    "accent_muted": "#FDDCB5",

    # Text
    "text":         "#202124",
    "text2":        "#6B7280",
    "text3":        "#9CA3AF",

    # Status
    "success":      "#16A34A",
    "success_bg":   "#F0FDF4",
    "warning":      "#D97706",
    "warning_bg":   "#FFFBEB",
    "danger":       "#DC2626",
    "danger_bg":    "#FEF2F2",

    # Borders & UI
    "border":       "#E5E7EB",
    "border_dark":  "#D1D5DB",
    "row_even":     "#F9FAFB",
    "hover":        "#F3F4F6",

    # Sidebar accent strip
    "nav_active_bg": "#FFF4ED",
    "nav_active_bar": "#F97316",
}

F = {
    "logo_name":  ("Segoe UI", 15, "bold"),
    "logo_sub":   ("Segoe UI", 8),
    "nav":        ("Segoe UI", 10),
    "nav_active": ("Segoe UI", 10, "bold"),
    "section":    ("Segoe UI", 7, "bold"),

    "h1":         ("Segoe UI", 20, "bold"),
    "h2":         ("Segoe UI", 15, "bold"),
    "h3":         ("Segoe UI", 12, "bold"),
    "h4":         ("Segoe UI", 10, "bold"),

    "card_value": ("Segoe UI", 26, "bold"),
    "card_label": ("Segoe UI", 9),

    "body":       ("Segoe UI", 10),
    "body_b":     ("Segoe UI", 10, "bold"),
    "small":      ("Segoe UI", 9),
    "small_b":    ("Segoe UI", 9, "bold"),
    "caption":    ("Segoe UI", 8),
    "caption_b":  ("Segoe UI", 8, "bold"),

    "mono":       ("Consolas", 9),
    "mono_b":     ("Consolas", 9, "bold"),

    "badge":      ("Segoe UI", 8, "bold"),
    "stat_val":   ("Segoe UI", 13, "bold"),
    "stat_lbl":   ("Segoe UI", 8),
}

VERSION = "2.0.0"
SIDEBAR_W = 240


# ══════════════════════════════════════════════════════════════
# REUSABLE PRIMITIVE WIDGETS
# ══════════════════════════════════════════════════════════════

class ScrollableFrame(tk.Frame):
    """Vertically scrollable container. Add content to self.inner."""

    def __init__(self, parent, bg=None, **kw):
        bg = bg or C["bg"]
        super().__init__(parent, bg=bg, **kw)

        self._canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self._vsb    = ttk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self.inner   = tk.Frame(self._canvas, bg=bg)

        self._win_id = self._canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self._canvas.configure(yscrollcommand=self._vsb.set)

        self._vsb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self.inner.bind("<Configure>", self._on_inner)
        self._canvas.bind("<Configure>", self._on_canvas)
        self._canvas.bind("<Enter>", lambda e: self._canvas.bind_all("<MouseWheel>", self._scroll))
        self._canvas.bind("<Leave>", lambda e: self._canvas.unbind_all("<MouseWheel>"))

    def _on_inner(self, _=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas(self, e):
        self._canvas.itemconfig(self._win_id, width=e.width)

    def _scroll(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")


def make_card(parent, padx=24, pady=20, bg=None):
    """
    Returns (border_frame, content_frame).
    Pack/grid border_frame; add widgets into content_frame.
    """
    bg = bg or C["card"]
    border = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
    content = tk.Frame(border, bg=bg, padx=padx, pady=pady)
    content.pack(fill="both", expand=True)
    return border, content


def hsep(parent, padx=0, color=None):
    """Thin horizontal rule."""
    f = tk.Frame(parent, height=1, bg=color or C["border"])
    f.pack(fill="x", padx=padx)
    return f


def vsep(parent, pady=0, color=None):
    """Thin vertical rule."""
    f = tk.Frame(parent, width=1, bg=color or C["border"])
    f.pack(side="left", fill="y", pady=pady)
    return f


def pill_label(parent, text, fg, bg, font=None, padx=8, pady=3):
    """Small colored badge / pill."""
    return tk.Label(
        parent, text=text,
        font=font or F["badge"],
        fg=fg, bg=bg,
        padx=padx, pady=pady,
    )


def section_heading(parent, text, subtitle="", bg=None):
    """Page-level title block."""
    bg = bg or C["bg"]
    blk = tk.Frame(parent, bg=bg)
    blk.pack(fill="x", padx=32, pady=(28, 20))
    tk.Label(blk, text=text, font=F["h1"], fg=C["text"], bg=bg).pack(anchor="w")
    if subtitle:
        tk.Label(blk, text=subtitle, font=F["small"], fg=C["text2"], bg=bg).pack(anchor="w", pady=(3, 0))
    return blk


def card_heading(parent, title, subtitle="", bg=None):
    """Card-level heading."""
    bg = bg or C["card"]
    tk.Label(parent, text=title, font=F["h3"], fg=C["text"], bg=bg).pack(anchor="w")
    if subtitle:
        tk.Label(parent, text=subtitle, font=F["small"], fg=C["text2"], bg=bg).pack(anchor="w", pady=(3, 0))


# ══════════════════════════════════════════════════════════════
# CANVAS HELPERS — drawn UI elements that ttk can't do cleanly
# ══════════════════════════════════════════════════════════════

def draw_rounded_bar(canvas, x0, y0, x1, y1, r, fill, outline=""):
    """Draw a rectangle with rounded corners on a tk.Canvas."""
    canvas.create_arc(x0, y0, x0 + 2*r, y0 + 2*r, start=90,  extent=90,  fill=fill, outline=outline)
    canvas.create_arc(x1 - 2*r, y0, x1, y0 + 2*r, start=0,   extent=90,  fill=fill, outline=outline)
    canvas.create_arc(x0, y1 - 2*r, x0 + 2*r, y1, start=180, extent=90,  fill=fill, outline=outline)
    canvas.create_arc(x1 - 2*r, y1 - 2*r, x1, y1, start=270, extent=90,  fill=fill, outline=outline)
    canvas.create_rectangle(x0 + r, y0, x1 - r, y1, fill=fill, outline=outline)
    canvas.create_rectangle(x0, y0 + r, x1, y1 - r, fill=fill, outline=outline)


# ══════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════

class PySentinelApp:
    """
    Premium PySentinel desktop application.

    Layout:
      Root window
      ├── Sidebar   (left, fixed 240 px)
      └── Main area (right, flexible)
          ├── Header (fixed height)
          └── Page container (stacked pages)
      └── Footer (bottom, full width)
    """

    # ── Initialisation ────────────────────────────────────────

    def __init__(self, root: tk.Tk):
        self.root = root

        # State variables
        self.sv_datetime  = tk.StringVar()
        self.sv_folder    = tk.StringVar(value="No folder selected")
        self.sv_status    = tk.StringVar(value="Ready to scan")
        self.sv_health    = tk.StringVar(value="Idle")
        self.sv_metrics   = {
            "total":  tk.StringVar(value="—"),
            "used":   tk.StringVar(value="—"),
            "free":   tk.StringVar(value="—"),
            "folder": tk.StringVar(value="—"),
        }

        # Scan state
        self._scanning   = False
        self._scan_data  = dict(
            total_gb=0.0, used_gb=0.0, free_gb=0.0,
            free_pct=0.0, folder_bytes=0, top_files=[],
        )
        self._health_color = C["text2"]

        # Paths
        self._dir       = os.path.dirname(os.path.abspath(__file__))
        self._log_path  = os.path.join(self._dir, "health_log.txt")
        self._disk_root = (os.path.splitdrive(self._dir)[0] + "\\") or "/"

        # Build
        self._setup_window()
        self._setup_styles()
        self._build_layout()
        self._load_initial_disk()
        self._tick_clock()

    # ── Window ────────────────────────────────────────────────

    def _setup_window(self):
        self.root.title("PySentinel — System Health Snapshot")
        self.root.configure(bg=C["white"])
        self.root.minsize(1060, 680)

        W, H = 1360, 820
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x  = max(0, (sw - W) // 2)
        y  = max(0, (sh - H) // 2)
        self.root.geometry(f"{W}x{H}+{x}+{y}")

    # ── ttk Styles ────────────────────────────────────────────

    def _setup_styles(self):
        s = ttk.Style()
        try:
            s.theme_use("clam")
        except Exception:
            pass

        # Scrollbar — minimal
        s.configure("Vertical.TScrollbar",
                     background=C["border"], troughcolor=C["bg"],
                     arrowcolor=C["text3"], borderwidth=0, relief="flat")

        # Progress bar — orange rounded look
        s.configure(
            "PS.Horizontal.TProgressbar",
            troughcolor=C["border"],
            background=C["accent"],
            bordercolor=C["border"],
            lightcolor=C["accent"],
            darkcolor=C["accent"],
            thickness=10,
        )

        # Files treeview
        s.configure(
            "PS.Treeview",
            background=C["card"],
            foreground=C["text"],
            fieldbackground=C["card"],
            font=F["body"],
            rowheight=42,
            borderwidth=0,
        )
        s.configure(
            "PS.Treeview.Heading",
            background=C["bg"],
            foreground=C["text2"],
            font=F["caption_b"],
            relief="flat",
            padding=(10, 10),
        )
        s.map("PS.Treeview",
              background=[("selected", C["accent_light"])],
              foreground=[("selected", C["accent_dark"])])
        s.map("PS.Treeview.Heading",
              background=[("active", C["hover"])])

        # History treeview
        s.configure(
            "Hist.Treeview",
            background=C["card"],
            foreground=C["text"],
            fieldbackground=C["card"],
            font=F["mono"],
            rowheight=36,
            borderwidth=0,
        )
        s.configure(
            "Hist.Treeview.Heading",
            background=C["bg"],
            foreground=C["text2"],
            font=F["caption_b"],
            relief="flat",
            padding=(10, 8),
        )
        s.map("Hist.Treeview",
              background=[("selected", C["accent_light"])],
              foreground=[("selected", C["accent_dark"])])
        s.map("Hist.Treeview.Heading",
              background=[("active", C["hover"])])

    # ══════════════════════════════════════════════════════════
    # LAYOUT SKELETON
    # ══════════════════════════════════════════════════════════

    def _build_layout(self):
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        self._build_sidebar()
        self._build_main()
        self._build_footer()

    # ══════════════════════════════════════════════════════════
    # SIDEBAR
    # ══════════════════════════════════════════════════════════

    def _build_sidebar(self):
        self._sidebar = tk.Frame(
            self.root, bg=C["sidebar"], width=SIDEBAR_W,
            highlightbackground=C["border"], highlightthickness=1,
        )
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)

        # ── Logo ──────────────────────────────────────────────
        logo_area = tk.Frame(self._sidebar, bg=C["sidebar"])
        logo_area.pack(fill="x", padx=22, pady=(30, 24))

        # Icon box
        ico_box = tk.Frame(logo_area, bg=C["accent"], padx=10, pady=8)
        ico_box.pack(anchor="w")
        tk.Label(ico_box, text="⚡", font=("Segoe UI", 18),
                 fg=C["white"], bg=C["accent"]).pack()

        name_row = tk.Frame(logo_area, bg=C["sidebar"])
        name_row.pack(fill="x", pady=(12, 0))
        tk.Label(name_row, text="PySentinel",
                 font=F["logo_name"], fg=C["text"], bg=C["sidebar"]).pack(anchor="w")
        tk.Label(name_row, text="System Health Snapshot",
                 font=F["logo_sub"], fg=C["text3"], bg=C["sidebar"]).pack(anchor="w", pady=(2, 0))

        hsep(self._sidebar, padx=22)

        # ── Nav section label ─────────────────────────────────
        tk.Label(
            self._sidebar, text="MAIN MENU",
            font=F["section"], fg=C["text3"],
            bg=C["sidebar"], anchor="w", padx=22,
        ).pack(fill="x", pady=(18, 6))

        # ── Nav items ─────────────────────────────────────────
        self._nav_btns   = {}
        self._active_page = "dashboard"

        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("storage",   "💾", "Storage Analysis"),
            ("files",     "📁", "Largest Files"),
            ("history",   "🕒", "Scan History"),
            ("about",     "ℹ️",  "About"),
        ]
        for pid, ico, lbl in nav_items:
            self._nav_btns[pid] = self._make_nav_btn(pid, ico, lbl)

        # ── Status card ───────────────────────────────────────
        hsep(self._sidebar, padx=22)

        sc = tk.Frame(self._sidebar, bg=C["sidebar"], padx=22, pady=16)
        sc.pack(fill="x")

        tk.Label(sc, text="SYSTEM STATUS", font=F["section"],
                 fg=C["text3"], bg=C["sidebar"]).pack(anchor="w")

        status_row = tk.Frame(sc, bg=C["sidebar"])
        status_row.pack(fill="x", pady=(8, 0))

        self._sidebar_dot = tk.Label(status_row, text="●",
                                     font=("Segoe UI", 10), fg=C["text3"], bg=C["sidebar"])
        self._sidebar_dot.pack(side="left")

        self._sidebar_status = tk.Label(
            status_row, textvariable=self.sv_health,
            font=F["body_b"], fg=C["text"], bg=C["sidebar"],
        )
        self._sidebar_status.pack(side="left", padx=(5, 0))

        # ── Version ───────────────────────────────────────────
        tk.Label(
            self._sidebar,
            text=f"v{VERSION}  ·  Python 3",
            font=F["caption"], fg=C["text3"], bg=C["sidebar"],
        ).pack(side="bottom", pady=14)

    def _make_nav_btn(self, pid, ico, lbl):
        """One sidebar navigation row."""
        outer = tk.Frame(self._sidebar, bg=C["sidebar"], cursor="hand2")
        outer.pack(fill="x", padx=0, pady=1)

        # Active indicator strip (left border)
        bar = tk.Frame(outer, width=3, bg=C["sidebar"])
        bar.pack(side="left", fill="y")

        inner = tk.Frame(outer, bg=C["sidebar"], padx=14, pady=10)
        inner.pack(fill="x", side="left", expand=True)

        ico_lbl = tk.Label(inner, text=ico, font=("Segoe UI", 12),
                           bg=C["sidebar"], width=2, anchor="center")
        ico_lbl.pack(side="left")

        txt_lbl = tk.Label(inner, text=lbl, font=F["nav"],
                           fg=C["text2"], bg=C["sidebar"], anchor="w")
        txt_lbl.pack(side="left", padx=(10, 0))

        all_w = [outer, inner, ico_lbl, txt_lbl]
        for w in all_w:
            w.bind("<Button-1>", lambda e, p=pid: self.show_page(p))

        def on_enter(e):
            if pid != self._active_page:
                for w in all_w: w.configure(bg=C["hover"])
                bar.configure(bg=C["hover"])
        def on_leave(e):
            if pid != self._active_page:
                for w in all_w: w.configure(bg=C["sidebar"])
                bar.configure(bg=C["sidebar"])

        for w in all_w:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)

        # Store refs
        outer._bar     = bar
        outer._inner   = inner
        outer._ico_lbl = ico_lbl
        outer._txt_lbl = txt_lbl
        return outer

    # ══════════════════════════════════════════════════════════
    # MAIN AREA
    # ══════════════════════════════════════════════════════════

    def _build_main(self):
        main = tk.Frame(self.root, bg=C["bg"])
        main.grid(row=0, column=1, sticky="nsew")
        main.grid_rowconfigure(0, weight=0)
        main.grid_rowconfigure(1, weight=1)
        main.grid_columnconfigure(0, weight=1)

        self._build_header(main)
        self._build_pages(main)

    # ── Header ────────────────────────────────────────────────

    def _build_header(self, parent):
        hdr = tk.Frame(
            parent, bg=C["white"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        hdr.grid(row=0, column=0, sticky="ew")

        inner = tk.Frame(hdr, bg=C["white"], padx=32, pady=16)
        inner.pack(fill="x")

        # Left — greeting + clock
        left = tk.Frame(inner, bg=C["white"])
        left.pack(side="left")

        tk.Label(left, text="Welcome to PySentinel",
                 font=F["h2"], fg=C["text"], bg=C["white"]).pack(anchor="w")
        tk.Label(left, textvariable=self.sv_datetime,
                 font=F["small"], fg=C["text2"], bg=C["white"]).pack(anchor="w", pady=(3, 0))

        # Right — health pill + scan button
        right = tk.Frame(inner, bg=C["white"])
        right.pack(side="right", anchor="center")

        # Health status pill
        self._hdr_badge_frame = tk.Frame(right, bg=C["bg"], padx=12, pady=6)
        self._hdr_badge_frame.pack(side="left", padx=(0, 16))

        self._hdr_dot = tk.Label(self._hdr_badge_frame, text="●",
                                 font=("Segoe UI", 9), fg=C["text3"], bg=C["bg"])
        self._hdr_dot.pack(side="left")
        self._hdr_status_lbl = tk.Label(
            self._hdr_badge_frame, textvariable=self.sv_health,
            font=F["small_b"], fg=C["text2"], bg=C["bg"],
        )
        self._hdr_status_lbl.pack(side="left", padx=(5, 0))

        # Scan button
        self._scan_btn = tk.Button(
            right,
            text="  🔍  Scan Folder  ",
            font=F["body_b"],
            bg=C["accent"], fg=C["white"],
            activebackground=C["accent_dark"], activeforeground=C["white"],
            relief="flat", cursor="hand2",
            padx=16, pady=9,
            command=self._start_scan,
        )
        self._scan_btn.pack(side="left")
        self._scan_btn.bind("<Enter>", lambda e: self._scan_btn.config(bg=C["accent_dark"]))
        self._scan_btn.bind("<Leave>", lambda e: self._scan_btn.config(bg=C["accent"]))

    # ══════════════════════════════════════════════════════════
    # PAGES CONTAINER
    # ══════════════════════════════════════════════════════════

    def _build_pages(self, parent):
        container = tk.Frame(parent, bg=C["bg"])
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self._container = container

        self._pages = {
            "dashboard": self._build_dashboard(),
            "storage":   self._build_storage(),
            "files":     self._build_files(),
            "history":   self._build_history(),
            "about":     self._build_about(),
        }

        for p in self._pages.values():
            p.grid(row=0, column=0, sticky="nsew")

        self.show_page("dashboard")

    def show_page(self, pid: str):
        """Hide all pages, raise the requested one, update nav."""
        self._active_page = pid

        for page in self._pages.values():
            page.grid_remove()
        self._pages[pid].grid()

        # Update nav button visual states
        for name, btn in self._nav_btns.items():
            active = (name == pid)
            if active:
                btn.configure(bg=C["nav_active_bg"])
                btn._bar.configure(bg=C["nav_active_bar"])
                btn._inner.configure(bg=C["nav_active_bg"])
                btn._ico_lbl.configure(bg=C["nav_active_bg"])
                btn._txt_lbl.configure(bg=C["nav_active_bg"],
                                       fg=C["accent"], font=F["nav_active"])
            else:
                btn.configure(bg=C["sidebar"])
                btn._bar.configure(bg=C["sidebar"])
                btn._inner.configure(bg=C["sidebar"])
                btn._ico_lbl.configure(bg=C["sidebar"])
                btn._txt_lbl.configure(bg=C["sidebar"],
                                       fg=C["text2"], font=F["nav"])

        if pid == "history":
            self._refresh_history()

    # ══════════════════════════════════════════════════════════
    # PAGE: DASHBOARD
    # ══════════════════════════════════════════════════════════

    def _build_dashboard(self) -> ScrollableFrame:
        sf = ScrollableFrame(self._container, bg=C["bg"])
        f  = sf.inner

        section_heading(f, "Dashboard",
                         "Real-time overview of your system's storage health")

        # ── 4 Metric Cards ────────────────────────────────────
        cards_frame = tk.Frame(f, bg=C["bg"])
        cards_frame.pack(fill="x", padx=32, pady=(0, 22))

        card_specs = [
            ("total",  "💾", "Total Storage",   C["accent"],    C["accent_light"]),
            ("used",   "📈", "Used Storage",    "#7C3AED",      "#F5F3FF"),
            ("free",   "✅", "Free Storage",    C["success"],   C["success_bg"]),
            ("folder", "📁", "Folder Size",     "#0369A1",      "#F0F9FF"),
        ]

        for i, (key, ico, lbl_text, color, ico_bg) in enumerate(card_specs):
            cards_frame.columnconfigure(i, weight=1, uniform="metric")
            self._make_metric_card(cards_frame, key, ico, lbl_text, color, ico_bg, col=i)

        # ── Disk Usage Card ───────────────────────────────────
        du_border, du_card = make_card(f, padx=28, pady=24)
        du_border.pack(fill="x", padx=32, pady=(0, 22))

        # Card header
        du_hdr = tk.Frame(du_card, bg=C["card"])
        du_hdr.pack(fill="x", pady=(0, 18))
        tk.Label(du_hdr, text="Disk Usage", font=F["h3"],
                 fg=C["text"], bg=C["card"]).pack(side="left")

        # Percentage labels right-aligned
        pct_frame = tk.Frame(du_hdr, bg=C["card"])
        pct_frame.pack(side="right")
        self._used_pct_lbl = tk.Label(pct_frame, text="Used: —",
                                       font=F["small_b"], fg=C["accent"], bg=C["card"])
        self._used_pct_lbl.pack(side="left", padx=(0, 16))
        self._free_pct_lbl = tk.Label(pct_frame, text="Free: —",
                                       font=F["small_b"], fg=C["success"], bg=C["card"])
        self._free_pct_lbl.pack(side="left")

        # Subtitle
        tk.Label(du_card, text="Overall storage distribution across your primary drive",
                 font=F["small"], fg=C["text2"], bg=C["card"]).pack(anchor="w", pady=(0, 16))

        # Canvas-drawn progress bar (rounded, two-tone)
        self._dash_bar_canvas = tk.Canvas(
            du_card, height=14, bg=C["card"],
            highlightthickness=0, bd=0,
        )
        self._dash_bar_canvas.pack(fill="x")
        self._dash_bar_canvas.bind("<Configure>", lambda e: self._draw_dash_bar())

        # Legend
        leg = tk.Frame(du_card, bg=C["card"])
        leg.pack(anchor="w", pady=(12, 0))
        for dot_color, label_text in [
            (C["accent"],  "Used"),
            (C["border"],  "Free"),
        ]:
            dot_row = tk.Frame(leg, bg=C["card"])
            dot_row.pack(side="left", padx=(0, 20))
            tk.Label(dot_row, text="●", font=("Segoe UI", 10),
                     fg=dot_color, bg=C["card"]).pack(side="left")
            tk.Label(dot_row, text=label_text, font=F["small"],
                     fg=C["text2"], bg=C["card"]).pack(side="left", padx=(4, 0))

        # ── Folder Analysis Card ──────────────────────────────
        fa_border, fa_card = make_card(f, padx=28, pady=24)
        fa_border.pack(fill="x", padx=32, pady=(0, 32))

        fa_hdr = tk.Frame(fa_card, bg=C["card"])
        fa_hdr.pack(fill="x", pady=(0, 16))
        tk.Label(fa_hdr, text="Folder Analysis", font=F["h3"],
                 fg=C["text"], bg=C["card"]).pack(side="left")

        # Path display area
        path_area = tk.Frame(fa_card, bg=C["bg"], padx=16, pady=12)
        path_area.pack(fill="x")

        path_top = tk.Frame(path_area, bg=C["bg"])
        path_top.pack(fill="x")
        tk.Label(path_top, text="SELECTED FOLDER",
                 font=F["section"], fg=C["text3"], bg=C["bg"]).pack(side="left")
        self._dash_folder_size = tk.Label(path_top, text="",
                                           font=F["small_b"], fg=C["accent"], bg=C["bg"])
        self._dash_folder_size.pack(side="right")

        tk.Label(path_area, textvariable=self.sv_folder,
                 font=F["mono"], fg=C["text"], bg=C["bg"],
                 wraplength=820, justify="left").pack(anchor="w", pady=(6, 0))

        # Status row
        status_row = tk.Frame(fa_card, bg=C["card"])
        status_row.pack(fill="x", pady=(14, 0))

        tk.Label(status_row, text="Status:", font=F["caption_b"],
                 fg=C["text3"], bg=C["card"]).pack(side="left")
        tk.Label(status_row, textvariable=self.sv_status,
                 font=F["small"], fg=C["text2"], bg=C["card"]).pack(side="left", padx=(6, 0))

        # Last scan timestamp label
        self._last_scan_lbl = tk.Label(status_row, text="",
                                        font=F["caption"], fg=C["text3"], bg=C["card"])
        self._last_scan_lbl.pack(side="right")

        return sf

    def _make_metric_card(self, parent, key, ico, label_text, color, ico_bg, col):
        """Single premium metric card."""
        gap = 0 if col == 3 else 16

        border = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        border.grid(row=0, column=col, padx=(0, gap), sticky="nsew", pady=4)

        inner = tk.Frame(border, bg=C["card"], padx=22, pady=20)
        inner.pack(fill="both", expand=True)

        # Top row: icon badge + accent stripe on card top would need a canvas,
        # so we use a small colored label for the icon
        top = tk.Frame(inner, bg=C["card"])
        top.pack(fill="x", pady=(0, 14))

        ico_cont = tk.Frame(top, bg=ico_bg, padx=8, pady=6)
        ico_cont.pack(side="left")
        tk.Label(ico_cont, text=ico, font=("Segoe UI", 14),
                 fg=color, bg=ico_bg).pack()

        # Value (big)
        tk.Label(inner, textvariable=self.sv_metrics[key],
                 font=F["card_value"], fg=color, bg=C["card"]).pack(anchor="w")

        # Label (small, uppercase)
        tk.Label(inner, text=label_text.upper(),
                 font=F["section"], fg=C["text3"], bg=C["card"]).pack(anchor="w", pady=(6, 0))

    def _draw_dash_bar(self):
        """Draw the rounded two-tone usage bar on the Dashboard."""
        c   = self._dash_bar_canvas
        c.delete("all")
        w = c.winfo_width()
        h = 14
        if w < 10:
            return

        r         = h // 2
        free_pct  = self._scan_data.get("free_pct", 0.0)
        used_pct  = 100.0 - free_pct
        used_px   = max(0, min(w, int(w * used_pct / 100)))

        # Background track
        draw_rounded_bar(c, 0, 0, w, h, r, C["border"])

        # Used portion (orange)
        if used_px > r * 2:
            draw_rounded_bar(c, 0, 0, used_px, h, r, C["accent"])
        elif used_px > 0:
            c.create_rectangle(0, 0, used_px, h, fill=C["accent"], outline="")

    # ══════════════════════════════════════════════════════════
    # PAGE: STORAGE ANALYSIS
    # ══════════════════════════════════════════════════════════

    def _build_storage(self) -> ScrollableFrame:
        sf = ScrollableFrame(self._container, bg=C["bg"])
        f  = sf.inner

        section_heading(f, "Storage Analysis",
                         "Detailed breakdown of your drive's storage distribution")

        # ── Drive Stats Card ──────────────────────────────────
        ds_border, ds_card = make_card(f, padx=28, pady=24)
        ds_border.pack(fill="x", padx=32, pady=(0, 22))

        card_heading(ds_card, "Drive Statistics",
                     "Live data fetched directly from your operating system")

        hsep(ds_card)
        ds_card.pack_slaves()[-1].pack(pady=(14, 16))  # give the separator breathing room

        # 3-column stats grid
        stat_grid = tk.Frame(ds_card, bg=C["card"])
        stat_grid.pack(fill="x")

        stat_defs = [
            ("DRIVE",       "s_drive",    C["text"]),
            ("TOTAL SPACE", "s_total",    C["text"]),
            ("USED SPACE",  "s_used",     "#7C3AED"),
            ("FREE SPACE",  "s_free",     C["success"]),
            ("USED %",      "s_used_pct", "#7C3AED"),
            ("FREE %",      "s_free_pct", C["success"]),
        ]

        for i, (name, attr, val_color) in enumerate(stat_defs):
            col = i % 3
            row = i // 3
            stat_grid.columnconfigure(col, weight=1, uniform="stat")

            cell = tk.Frame(stat_grid, bg=C["bg"], padx=16, pady=14)
            cell.grid(row=row, column=col, padx=(0 if col == 0 else 8, 0),
                      pady=(0, 8), sticky="nsew")

            tk.Label(cell, text=name, font=F["section"],
                     fg=C["text3"], bg=C["bg"]).pack(anchor="w")

            val_lbl = tk.Label(cell, text="—", font=F["stat_val"],
                               fg=val_color, bg=C["bg"])
            val_lbl.pack(anchor="w", pady=(4, 0))
            setattr(self, attr, val_lbl)

        # ── Visual Storage Distribution Card ──────────────────
        vd_border, vd_card = make_card(f, padx=28, pady=24)
        vd_border.pack(fill="x", padx=32, pady=(0, 22))

        card_heading(vd_card, "Storage Distribution",
                     "Visual breakdown of used vs. free disk space")

        # Spacer
        tk.Frame(vd_card, bg=C["card"], height=16).pack(fill="x")

        # Canvas for custom two-tone bar
        self._stor_canvas = tk.Canvas(
            vd_card, height=36, bg=C["card"],
            highlightthickness=0, bd=0,
        )
        self._stor_canvas.pack(fill="x")
        self._stor_canvas.bind("<Configure>", lambda e: self._draw_storage_bar())

        # Percentage labels below the bar
        pct_row = tk.Frame(vd_card, bg=C["card"])
        pct_row.pack(fill="x", pady=(10, 0))
        self._stor_used_lbl = tk.Label(pct_row, text="Used: —",
                                        font=F["small_b"], fg=C["accent"], bg=C["card"])
        self._stor_used_lbl.pack(side="left")
        self._stor_free_lbl = tk.Label(pct_row, text="Free: —",
                                        font=F["small_b"], fg=C["success"], bg=C["card"])
        self._stor_free_lbl.pack(side="right")

        # Legend
        leg = tk.Frame(vd_card, bg=C["card"])
        leg.pack(anchor="w", pady=(10, 0))
        for dot_c, lbl_t in [(C["accent"], "Used Storage"), (C["border_dark"], "Free Storage")]:
            row = tk.Frame(leg, bg=C["card"])
            row.pack(side="left", padx=(0, 24))
            tk.Label(row, text="■", font=("Segoe UI", 10),
                     fg=dot_c, bg=C["card"]).pack(side="left")
            tk.Label(row, text=lbl_t, font=F["small"],
                     fg=C["text2"], bg=C["card"]).pack(side="left", padx=(4, 0))

        # ── Health Recommendation Card ─────────────────────────
        hr_border, hr_card = make_card(f, padx=28, pady=24)
        hr_border.pack(fill="x", padx=32, pady=(0, 32))

        card_heading(hr_card, "Storage Health",
                     "Personalised recommendation based on your current disk usage")

        tk.Frame(hr_card, bg=C["card"], height=12).pack(fill="x")

        self._health_tip_frame = tk.Frame(hr_card, bg=C["bg"], padx=16, pady=14)
        self._health_tip_frame.pack(fill="x")

        self._health_tip = tk.Label(
            self._health_tip_frame,
            text="Run a scan to receive personalised storage health recommendations.",
            font=F["body"], fg=C["text2"], bg=C["bg"],
            wraplength=820, justify="left",
        )
        self._health_tip.pack(anchor="w")

        return sf

    def _draw_storage_bar(self):
        """Redraw the storage distribution bar on the Storage Analysis page."""
        c = self._stor_canvas
        c.delete("all")
        w  = c.winfo_width()
        h  = 36
        if w < 10:
            return

        r         = h // 2
        free_pct  = self._scan_data.get("free_pct", 0.0)
        used_pct  = 100.0 - free_pct
        used_px   = max(0, min(w, int(w * used_pct / 100)))
        free_px   = w - used_px

        # Full track (free — grey)
        draw_rounded_bar(c, 0, 0, w, h, r, C["border_dark"])

        # Used (orange) — clipped on right, so draw as rectangle if not covering full bar
        if used_px >= w:
            draw_rounded_bar(c, 0, 0, w, h, r, C["accent"])
        elif used_px > r * 2:
            draw_rounded_bar(c, 0, 0, used_px, h, r, C["accent"])
        elif used_px > 0:
            c.create_rectangle(0, 0, used_px, h, fill=C["accent"], outline="")

        # Text inside bar
        if used_px > 60:
            c.create_text(
                used_px // 2, h // 2,
                text=f"{used_pct:.1f}%",
                fill=C["white"], font=F["small_b"],
            )
        if free_px > 60:
            c.create_text(
                used_px + free_px // 2, h // 2,
                text=f"{free_pct:.1f}%",
                fill=C["white"] if used_px >= w else C["text"],
                font=F["small_b"],
            )

    # ══════════════════════════════════════════════════════════
    # PAGE: LARGEST FILES
    # ══════════════════════════════════════════════════════════

    def _build_files(self) -> ScrollableFrame:
        sf = ScrollableFrame(self._container, bg=C["bg"])
        f  = sf.inner

        section_heading(f, "Largest Files",
                         "Top 5 largest files discovered in your scanned folder")

        tbl_border, tbl_card = make_card(f, padx=0, pady=0)
        tbl_border.pack(fill="x", padx=32, pady=(0, 32))

        # Card header inside padded sub-frame
        tbl_hdr = tk.Frame(tbl_card, bg=C["card"], padx=24, pady=20)
        tbl_hdr.pack(fill="x")
        tk.Label(tbl_hdr, text="File Rankings",
                 font=F["h3"], fg=C["text"], bg=C["card"]).pack(side="left")
        self._files_count_lbl = tk.Label(tbl_hdr, text="",
                                          font=F["small"], fg=C["text3"], bg=C["card"])
        self._files_count_lbl.pack(side="right")

        hsep(tbl_card)

        # Empty state
        self._files_empty = tk.Frame(tbl_card, bg=C["card"], pady=60)
        self._files_empty.pack(fill="x")
        tk.Label(self._files_empty, text="📁",
                 font=("Segoe UI", 32), fg=C["border_dark"], bg=C["card"]).pack()
        tk.Label(self._files_empty, text="No files scanned yet",
                 font=F["h3"], fg=C["text3"], bg=C["card"]).pack(pady=(8, 0))
        tk.Label(self._files_empty,
                 text="Click  🔍 Scan Folder  to discover the largest files in a directory.",
                 font=F["small"], fg=C["text3"], bg=C["card"]).pack(pady=(4, 0))

        # Treeview (hidden until first scan)
        cols = ("rank", "name", "size", "type", "location")
        self._files_tree = ttk.Treeview(
            tbl_card, columns=cols, show="headings",
            style="PS.Treeview", height=12, selectmode="browse",
        )

        col_specs = [
            ("rank",     "#",         50,  "center"),
            ("name",     "File Name", 240, "w"),
            ("size",     "Size",      110, "center"),
            ("type",     "Type",      110, "center"),
            ("location", "Location",  0,   "w"),     # 0 = stretches
        ]
        for cid, heading, width, anch in col_specs:
            self._files_tree.heading(cid, text=heading.upper())
            kw = {"width": width, "anchor": anch, "minwidth": 40}
            if width == 0:
                kw["stretch"] = True
            else:
                kw["stretch"] = False
            self._files_tree.column(cid, **kw)

        self._files_tree.tag_configure("odd",  background=C["card"])
        self._files_tree.tag_configure("even", background=C["row_even"])

        self._files_vsb = ttk.Scrollbar(tbl_card, orient="vertical",
                                         command=self._files_tree.yview)
        self._files_tree.configure(yscrollcommand=self._files_vsb.set)

        return sf

    # ══════════════════════════════════════════════════════════
    # PAGE: SCAN HISTORY
    # ══════════════════════════════════════════════════════════

    def _build_history(self) -> ScrollableFrame:
        sf = ScrollableFrame(self._container, bg=C["bg"])
        f  = sf.inner

        section_heading(f, "Scan History",
                         "All previous scan records stored in health_log.txt")

        h_border, h_card = make_card(f, padx=0, pady=0)
        h_border.pack(fill="x", padx=32, pady=(0, 32))

        # Card header
        h_hdr = tk.Frame(h_card, bg=C["card"], padx=24, pady=20)
        h_hdr.pack(fill="x")
        tk.Label(h_hdr, text="Scan Records",
                 font=F["h3"], fg=C["text"], bg=C["card"]).pack(side="left")

        refresh_btn = tk.Button(
            h_hdr, text="↻  Refresh",
            font=F["small_b"], fg=C["accent"], bg=C["accent_light"],
            activebackground=C["accent_muted"], activeforeground=C["accent"],
            relief="flat", cursor="hand2", padx=10, pady=4,
            command=self._refresh_history,
        )
        refresh_btn.pack(side="right")

        self._hist_count_lbl = tk.Label(h_hdr, text="",
                                         font=F["small"], fg=C["text3"], bg=C["card"])
        self._hist_count_lbl.pack(side="right", padx=(0, 14))

        hsep(h_card)

        # Empty state
        self._hist_empty = tk.Frame(h_card, bg=C["card"], pady=60)
        tk.Label(self._hist_empty, text="🕒",
                 font=("Segoe UI", 32), fg=C["border_dark"], bg=C["card"]).pack()
        tk.Label(self._hist_empty, text="No scan history yet",
                 font=F["h3"], fg=C["text3"], bg=C["card"]).pack(pady=(8, 0))
        tk.Label(self._hist_empty,
                 text="Run your first scan to begin logging.",
                 font=F["small"], fg=C["text3"], bg=C["card"]).pack(pady=(4, 0))

        # Treeview
        h_cols = ("ts", "total", "used", "free_gb", "free_pct", "folder", "fsize")
        self._hist_tree = ttk.Treeview(
            h_card, columns=h_cols, show="headings",
            style="Hist.Treeview", height=16, selectmode="browse",
        )

        h_col_specs = [
            ("ts",       "TIMESTAMP",         170, "w"),
            ("total",    "TOTAL",              90, "center"),
            ("used",     "USED",               90, "center"),
            ("free_gb",  "FREE",               90, "center"),
            ("free_pct", "FREE %",             70, "center"),
            ("folder",   "FOLDER SCANNED",      0, "w"),
            ("fsize",    "FOLDER SIZE",        110, "center"),
        ]
        for cid, heading, width, anch in h_col_specs:
            self._hist_tree.heading(cid, text=heading)
            kw = {"anchor": anch, "minwidth": 40}
            if width == 0:
                kw["stretch"] = True
                kw["width"]   = 200
            else:
                kw["width"]   = width
                kw["stretch"] = False
            self._hist_tree.column(cid, **kw)

        self._hist_tree.tag_configure("odd",  background=C["card"])
        self._hist_tree.tag_configure("even", background=C["row_even"])

        hist_vsb = ttk.Scrollbar(h_card, orient="vertical",
                                  command=self._hist_tree.yview)
        self._hist_tree.configure(yscrollcommand=hist_vsb.set)

        hist_vsb.pack(side="right", fill="y")
        self._hist_tree.pack(fill="both", expand=True, padx=1, pady=1)

        return sf

    # ══════════════════════════════════════════════════════════
    # PAGE: ABOUT
    # ══════════════════════════════════════════════════════════

    def _build_about(self) -> ScrollableFrame:
        sf = ScrollableFrame(self._container, bg=C["bg"])
        f  = sf.inner

        section_heading(f, "About PySentinel",
                         "Project details, features and SkillMe internship information")

        # ── Identity Card ─────────────────────────────────────
        id_border, id_card = make_card(f, padx=32, pady=28)
        id_border.pack(fill="x", padx=32, pady=(0, 22))

        # Logo row
        logo_row = tk.Frame(id_card, bg=C["card"])
        logo_row.pack(fill="x", pady=(0, 20))

        ico_box = tk.Frame(logo_row, bg=C["accent"], padx=14, pady=12)
        ico_box.pack(side="left")
        tk.Label(ico_box, text="⚡", font=("Segoe UI", 28),
                 fg=C["white"], bg=C["accent"]).pack()

        name_col = tk.Frame(logo_row, bg=C["card"])
        name_col.pack(side="left", padx=(18, 0))
        tk.Label(name_col, text="PySentinel",
                 font=F["h1"], fg=C["text"], bg=C["card"]).pack(anchor="w")

        badge_row = tk.Frame(name_col, bg=C["card"])
        badge_row.pack(anchor="w", pady=(6, 0))
        pill_label(badge_row, f"v{VERSION}", C["accent"], C["accent_light"]).pack(side="left")
        tk.Label(badge_row, text="·", font=F["body"], fg=C["text3"], bg=C["card"]).pack(
            side="left", padx=8)
        pill_label(badge_row, "System Health Snapshot", C["text2"], C["bg"]).pack(side="left")

        hsep(id_card)

        # Description
        tk.Label(
            id_card,
            text=(
                "PySentinel is a Python-powered desktop tool for monitoring your computer's "
                "storage health. Built as the Week 1 assignment for the SkillMe Python Technical "
                "Internship, it uses only Python's standard library — no third-party packages required."
            ),
            font=F["body"], fg=C["text"], bg=C["card"],
            wraplength=820, justify="left",
        ).pack(anchor="w", pady=(18, 18))

        hsep(id_card)

        # ── Features ─────────────────────────────────────────
        tk.Label(id_card, text="Core Features",
                 font=F["h3"], fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(18, 12))

        features = [
            ("💾", "Disk Usage Statistics",   "Total, used and free space via shutil.disk_usage()"),
            ("📁", "Folder Scanner",          "Deep recursive scan using os.walk() with error handling"),
            ("📊", "Top 5 Largest Files",     "Sorted by size with file type and location details"),
            ("📋", "Timestamped Reports",     "Readable system health reports generated with datetime"),
            ("🕒", "Persistent Scan Log",     "health_log.txt — entries appended, never erased"),
            ("🛡️", "Graceful Error Handling",  "PermissionError and OSError caught silently per file"),
            ("🎨", "Modern GUI",              "Premium white-and-orange tkinter interface"),
        ]

        feat_grid = tk.Frame(id_card, bg=C["card"])
        feat_grid.pack(fill="x")

        for i, (ico, title, desc) in enumerate(features):
            col = i % 2
            row = i // 2
            feat_grid.columnconfigure(col, weight=1, uniform="feat")

            cell = tk.Frame(feat_grid, bg=C["bg"], padx=16, pady=12)
            cell.grid(row=row, column=col,
                      padx=(0, 10) if col == 0 else 0,
                      pady=(0, 10), sticky="nsew")

            top_r = tk.Frame(cell, bg=C["bg"])
            top_r.pack(fill="x")
            tk.Label(top_r, text=ico, font=("Segoe UI", 13),
                     bg=C["bg"]).pack(side="left")
            tk.Label(top_r, text=title, font=F["body_b"],
                     fg=C["text"], bg=C["bg"]).pack(side="left", padx=(8, 0))
            tk.Label(cell, text=desc, font=F["small"],
                     fg=C["text2"], bg=C["bg"], wraplength=360, justify="left").pack(anchor="w", pady=(4, 0))

        hsep(id_card)

        # ── Tech stack ────────────────────────────────────────
        tk.Label(id_card, text="Built With",
                 font=F["h3"], fg=C["text"], bg=C["card"]).pack(anchor="w", pady=(18, 10))

        tech_row = tk.Frame(id_card, bg=C["card"])
        tech_row.pack(anchor="w")
        for tech in ["Python 3.10+", "tkinter", "os", "shutil", "datetime", "threading"]:
            pill_label(
                tech_row, tech,
                C["accent"], C["accent_light"],
                padx=10, pady=5,
            ).pack(side="left", padx=(0, 8), pady=2)

        hsep(id_card)

        # ── Internship credit ─────────────────────────────────
        credit = tk.Frame(id_card, bg=C["bg"], padx=20, pady=16)
        credit.pack(fill="x", pady=(18, 0))

        cr_left = tk.Frame(credit, bg=C["bg"])
        cr_left.pack(side="left")
        tk.Label(cr_left, text="📚  SkillMe Python Technical Internship",
                 font=F["h3"], fg=C["text"], bg=C["bg"]).pack(anchor="w")
        tk.Label(cr_left, text="Assignment: Week 1 — System Health Snapshot",
                 font=F["body"], fg=C["text2"], bg=C["bg"]).pack(anchor="w", pady=(4, 0))

        # Pass badge
        pass_badge = tk.Frame(credit, bg=C["success_bg"], padx=14, pady=8)
        pass_badge.pack(side="right")
        tk.Label(pass_badge, text="✅  All 7 requirements implemented",
                 font=F["small_b"], fg=C["success"], bg=C["success_bg"]).pack()

        return sf

    # ══════════════════════════════════════════════════════════
    # FOOTER
    # ══════════════════════════════════════════════════════════

    def _build_footer(self):
        footer = tk.Frame(
            self.root, bg=C["white"],
            highlightbackground=C["border"], highlightthickness=1,
        )
        footer.grid(row=1, column=0, columnspan=2, sticky="ew")

        inner = tk.Frame(footer, bg=C["white"], padx=28, pady=10)
        inner.pack(fill="x")

        left = tk.Frame(inner, bg=C["white"])
        left.pack(side="left")
        tk.Label(left, text="⚡  PySentinel",
                 font=F["body_b"], fg=C["accent"], bg=C["white"]).pack(side="left")
        tk.Label(left, text=f"  v{VERSION}",
                 font=F["caption"], fg=C["text3"], bg=C["white"]).pack(side="left")

        right = tk.Frame(inner, bg=C["white"])
        right.pack(side="right")
        tk.Label(
            right,
            text="Python-Powered Application  ·  SkillMe Technical Internship  ·  Week 1",
            font=F["caption"], fg=C["text3"], bg=C["white"],
        ).pack(side="right")

    # ══════════════════════════════════════════════════════════
    # SCAN LOGIC
    # ══════════════════════════════════════════════════════════

    def _start_scan(self):
        """Open folder chooser and begin background scan."""
        if self._scanning:
            return

        folder = filedialog.askdirectory(
            title="PySentinel — Select a Folder to Scan",
            initialdir=os.path.expanduser("~"),
        )
        if not folder:
            return

        folder = os.path.normpath(folder)

        self._scanning = True
        self.sv_folder.set(folder)
        self.sv_status.set("Scanning — please wait…")
        self.sv_health.set("Scanning")
        self._set_health_color(C["warning"])
        self._scan_btn.configure(text="  ⏳  Scanning…  ", state="disabled", bg=C["text3"])

        threading.Thread(target=self._do_scan, args=(folder,), daemon=True).start()

    def _do_scan(self, folder: str):
        """Background worker. Calls monitor.py functions only."""
        try:
            total_gb, used_gb, free_gb = monitor.disk_usage(self._disk_root)
            free_pct     = round((free_gb / total_gb) * 100, 1)
            folder_bytes = monitor.folder_size(folder)
            top_files    = monitor.largest_files(folder, n=5)

            self._scan_data = dict(
                total_gb=total_gb, used_gb=used_gb, free_gb=free_gb,
                free_pct=free_pct, folder_bytes=folder_bytes, top_files=top_files,
            )

            monitor.log_scan(self._disk_root, folder, log_file=self._log_path)
            self.root.after(0, self._finish_scan)

        except Exception as exc:
            self.root.after(0, lambda msg=str(exc): self._handle_scan_error(msg))

    def _finish_scan(self):
        """Update every display widget once the scan completes."""
        d        = self._scan_data
        used_pct = round(100.0 - d["free_pct"], 1)
        now_str  = datetime.datetime.now().strftime("%H:%M:%S")

        # Metric cards
        self.sv_metrics["total"].set(f"{d['total_gb']} GB")
        self.sv_metrics["used"].set(f"{d['used_gb']} GB")
        self.sv_metrics["free"].set(f"{d['free_gb']} GB")
        self.sv_metrics["folder"].set(monitor.human_size(d["folder_bytes"]))

        # Dashboard bar
        self._used_pct_lbl.configure(text=f"Used: {d['used_gb']} GB  ({used_pct}%)")
        self._free_pct_lbl.configure(text=f"Free: {d['free_gb']} GB  ({d['free_pct']}%)")
        self.root.after(50, self._draw_dash_bar)

        # Dashboard folder card
        self._dash_folder_size.configure(text=monitor.human_size(d["folder_bytes"]))
        self._last_scan_lbl.configure(text=f"Last scan: {now_str}")

        # Storage page
        self.s_drive.configure(text=self._disk_root)
        self.s_total.configure(text=f"{d['total_gb']} GB")
        self.s_used.configure(text=f"{d['used_gb']} GB")
        self.s_free.configure(text=f"{d['free_gb']} GB")
        self.s_used_pct.configure(text=f"{used_pct}%")
        self.s_free_pct.configure(text=f"{d['free_pct']}%")
        self._stor_used_lbl.configure(text=f"Used: {d['used_gb']} GB  ({used_pct}%)")
        self._stor_free_lbl.configure(text=f"Free: {d['free_gb']} GB  ({d['free_pct']}%)")
        self.root.after(50, self._draw_storage_bar)

        # Health tip
        tip_text, tip_fg, tip_bg = self._get_tip(d["free_pct"])
        self._health_tip_frame.configure(bg=tip_bg)
        self._health_tip.configure(text=tip_text, fg=tip_fg, bg=tip_bg)

        # Largest files
        self._populate_files(d["top_files"])

        # Status
        self.sv_status.set(f"Scan complete — {now_str}")

        if d["free_pct"] < 10:
            status, color = "Critical", C["danger"]
        elif d["free_pct"] < 20:
            status, color = "Warning",  C["warning"]
        else:
            status, color = "Healthy",  C["success"]

        self.sv_health.set(status)
        self._set_health_color(color)

        # Re-enable scan button
        self._scan_btn.configure(text="  🔍  Scan Folder  ", state="normal", bg=C["accent"])
        self._scanning = False

    def _handle_scan_error(self, msg: str):
        self.sv_status.set("Scan failed")
        self.sv_health.set("Error")
        self._set_health_color(C["danger"])
        self._scan_btn.configure(text="  🔍  Scan Folder  ", state="normal", bg=C["accent"])
        self._scanning = False
        messagebox.showerror(
            "PySentinel — Scan Error",
            f"The scan could not be completed:\n\n{msg}",
        )

    # ── Helpers ───────────────────────────────────────────────

    def _set_health_color(self, color: str):
        """Update the health dot color in both the sidebar and header."""
        self._sidebar_dot.configure(fg=color)
        self._hdr_dot.configure(fg=color)
        self._hdr_status_lbl.configure(fg=color)

    def _populate_files(self, top_files: list):
        """Fill the largest-files Treeview."""
        for row in self._files_tree.get_children():
            self._files_tree.delete(row)

        if top_files:
            # Hide empty state, show table
            self._files_empty.pack_forget()
            self._files_vsb.pack(side="right", fill="y")
            self._files_tree.pack(fill="both", expand=True, padx=1, pady=1)

            self._files_count_lbl.configure(text=f"{len(top_files)} files found")

            for i, (size, fpath) in enumerate(top_files, start=1):
                name = os.path.basename(fpath)
                loc  = os.path.dirname(fpath)
                tag  = "odd" if i % 2 else "even"
                self._files_tree.insert(
                    "", "end",
                    values=(i, name, monitor.human_size(size),
                            monitor.get_file_type(fpath), loc),
                    tags=(tag,),
                )
        else:
            self._files_tree.pack_forget()
            self._files_vsb.pack_forget()
            # Update empty state message
            for child in self._files_empty.winfo_children():
                if hasattr(child, "cget"):
                    try:
                        if child.cget("text") == "No files scanned yet":
                            child.configure(text="No files found")
                    except Exception:
                        pass
            self._files_empty.pack(fill="x")
            self._files_count_lbl.configure(text="")

    def _refresh_history(self):
        """Read health_log.txt and populate the history Treeview."""
        for row in self._hist_tree.get_children():
            self._hist_tree.delete(row)

        entries = []
        if os.path.exists(self._log_path):
            try:
                with open(self._log_path, "r", encoding="utf-8") as fh:
                    entries = [ln.strip() for ln in fh if ln.strip()]
            except Exception:
                pass

        if not entries:
            self._hist_tree.pack_forget()
            self._hist_empty.pack(fill="x", pady=60)
            self._hist_count_lbl.configure(text="")
            return

        self._hist_empty.pack_forget()
        self._hist_tree.pack(fill="both", expand=True, padx=1, pady=1)
        self._hist_count_lbl.configure(text=f"{len(entries)} records")

        # Parse newest-first
        for i, line in enumerate(reversed(entries)):
            try:
                ts     = line[1:20]
                parts  = line.split("|")
                disk_p = parts[0].split("Disk:")[-1].strip()
                total  = (disk_p.split("GB")[0].strip() + " GB") if "GB" in disk_p else "—"
                free_p = parts[1].split("Free:")[-1].strip()
                free_g = (free_p.split("GB")[0].strip() + " GB") if "GB" in free_p else "—"
                free_b = free_p[free_p.find("(")+1 : free_p.find(")")] if "(" in free_p else "—"
                folder = parts[2].split("Scanned:")[-1].strip()
                fsize  = parts[3].split("Folder Size:")[-1].strip()

                # Derive used from total and free
                try:
                    t_num = float(total.replace(" GB", ""))
                    f_num = float(free_g.replace(" GB", ""))
                    used  = f"{round(t_num - f_num, 2)} GB"
                except Exception:
                    used = "—"

                tag = "odd" if i % 2 else "even"
                self._hist_tree.insert(
                    "", "end",
                    values=(ts, total, used, free_g, free_b, folder, fsize),
                    tags=(tag,),
                )
            except Exception:
                tag = "odd" if i % 2 else "even"
                self._hist_tree.insert("", "end",
                                        values=("—", "—", "—", "—", "—", line, "—"),
                                        tags=(tag,))

    def _load_initial_disk(self):
        """Show disk stats immediately at startup, before any folder scan."""
        try:
            total_gb, used_gb, free_gb = monitor.disk_usage(self._disk_root)
            free_pct = round((free_gb / total_gb) * 100, 1)
            used_pct = round(100 - free_pct, 1)

            self._scan_data.update(
                total_gb=total_gb, used_gb=used_gb,
                free_gb=free_gb, free_pct=free_pct,
            )

            # Metric cards
            self.sv_metrics["total"].set(f"{total_gb} GB")
            self.sv_metrics["used"].set(f"{used_gb} GB")
            self.sv_metrics["free"].set(f"{free_gb} GB")

            # Dashboard bar labels
            self._used_pct_lbl.configure(text=f"Used: {used_gb} GB  ({used_pct}%)")
            self._free_pct_lbl.configure(text=f"Free: {free_gb} GB  ({free_pct}%)")

            # Storage page
            self.s_drive.configure(text=self._disk_root)
            self.s_total.configure(text=f"{total_gb} GB")
            self.s_used.configure(text=f"{used_gb} GB")
            self.s_free.configure(text=f"{free_gb} GB")
            self.s_used_pct.configure(text=f"{used_pct}%")
            self.s_free_pct.configure(text=f"{free_pct}%")
            self._stor_used_lbl.configure(text=f"Used: {used_gb} GB  ({used_pct}%)")
            self._stor_free_lbl.configure(text=f"Free: {free_gb} GB  ({free_pct}%)")

            # Health status
            if free_pct >= 20:
                status, color = "Healthy",  C["success"]
            elif free_pct >= 10:
                status, color = "Warning",  C["warning"]
            else:
                status, color = "Critical", C["danger"]

            self.sv_health.set(status)
            self._set_health_color(color)

            # Draw bars after window renders
            self.root.after(200, self._draw_dash_bar)
            self.root.after(220, self._draw_storage_bar)

        except Exception:
            pass

    def _get_tip(self, free_pct: float):
        """Return (text, fg_color, bg_color) for the health tip."""
        if free_pct >= 50:
            return (
                f"✅  Excellent! Your disk has {free_pct:.1f}% free space. "
                "Your system is running comfortably.",
                C["success"], C["success_bg"],
            )
        elif free_pct >= 25:
            return (
                f"✅  Good. Your disk has {free_pct:.1f}% free space. "
                "Review large files periodically to keep things tidy.",
                C["success"], C["success_bg"],
            )
        elif free_pct >= 10:
            return (
                f"⚠️  Moderate. Your disk has {free_pct:.1f}% free space. "
                "Consider deleting or archiving unused files.",
                C["warning"], C["warning_bg"],
            )
        else:
            return (
                f"🔴  Low disk space: only {free_pct:.1f}% free. "
                "This can slow down your computer. Delete unused files, "
                "empty the Recycle Bin, or move files to external storage now.",
                C["danger"], C["danger_bg"],
            )

    def _tick_clock(self):
        """Live clock — updates every second."""
        self.sv_datetime.set(
            datetime.datetime.now().strftime("%A, %d %B %Y  ·  %I:%M:%S %p")
        )
        self.root.after(1000, self._tick_clock)


# ══════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    root = tk.Tk()
    PySentinelApp(root)
    root.mainloop()
