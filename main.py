"""
CardMe – Windows Flashcard App
================================
INSTALLATION & START (Schritt-für-Schritt):
  1. Python installieren: https://www.python.org/downloads/  (Haken bei "Add to PATH" setzen!)
  2. Bibliothek installieren:  pip install customtkinter
  3. Diese Datei starten:      python main.py
"""

import customtkinter as ctk
import json
import os
import random
import shutil
import ctypes
import urllib.request
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

# ──────────────────────────────────────────────────────────────
# POPPINS FONT
# Sind die TTF-Dateien bereits vorhanden → sofort registrieren (kein Netzwerk).
# Fehlen sie → App startet sofort mit Segoe UI; Download läuft im Hintergrund.
# ──────────────────────────────────────────────────────────────
_FONT_URLS = {
    "Poppins-Regular.ttf":  "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Regular.ttf",
    "Poppins-Bold.ttf":     "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
    "Poppins-SemiBold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf",
}
_FONTS_DIR = os.path.join(os.path.expanduser("~"), ".cardme_fonts")

def _register_fonts() -> bool:
    """Registriert bereits vorhandene TTF-Dateien bei Windows. Gibt True zurück wenn alle da sind."""
    all_present = True
    for fname in _FONT_URLS:
        fpath = os.path.join(_FONTS_DIR, fname)
        if os.path.exists(fpath):
            try:
                ctypes.windll.gdi32.AddFontResourceExW(fpath, 0x10, 0)
            except Exception:
                pass
        else:
            all_present = False
    return all_present

def _download_fonts_background():
    """Lädt fehlende Poppins-Fonts im Hintergrund herunter (blockiert die App nicht)."""
    os.makedirs(_FONTS_DIR, exist_ok=True)
    for fname, url in _FONT_URLS.items():
        fpath = os.path.join(_FONTS_DIR, fname)
        if not os.path.exists(fpath):
            try:
                urllib.request.urlretrieve(url, fpath)
                ctypes.windll.gdi32.AddFontResourceExW(fpath, 0x10, 0)
            except Exception:
                pass

os.makedirs(_FONTS_DIR, exist_ok=True)
if _register_fonts():
    FONT = "Poppins"
else:
    FONT = "Segoe UI"
    threading.Thread(target=_download_fonts_background, daemon=True).start()

# ──────────────────────────────────────────────────────────────
# FARBEN  (Dunkelgrau · Blau · Rot – Icon-Palette)
# ──────────────────────────────────────────────────────────────
APP_TITLE    = "CardMe"
APP_W, APP_H = 860, 600

BG          = "#1A1A1A"   # Dunkles Grau – Haupt-BG
SIDEBAR_BG  = "#111111"   # Sehr dunkles Grau für Sidebar
CARD_BG     = "#252525"   # Karten-Hintergrund
SURFACE2    = "#2E2E2E"   # Eingabefelder / Sekundär

# Icon-Akzentfarben: Blau · Rot
BLUE        = "#3BBAE7"   # Helles Blau – NUR für Textakzente / Highlights
BLUE_HVR    = "#2AA8D8"   # Hover-Textakzent
BTN_PRIMARY = "#1A6EB5"   # Dunkleres Blau für Button-BG  (Kontrast auf Weiß ≈ 4.8:1)
BTN_HVR     = "#145A99"   # Hover Button-BG
RED         = "#EE362E"   # Rotakzent
RED_HVR     = "#C42020"   # Hover-Rot
WHITE       = "#FFFFFF"
TEXT_PRI    = "#FFFFFF"
TEXT_SEC    = "#777777"   # Sekundäres Grau
BORDER      = "#3A3A3A"   # Trennlinien

# Compat-Aliase  (YELLOW → dunkles Button-Blau, BLUE bleibt für Textakzente)
YELLOW      = BTN_PRIMARY
YELLOW_HVR  = BTN_HVR
SURFACE     = BG
ACCENT      = BLUE
ACCENT_HOVER= BLUE_HVR
ACCENT2     = WHITE

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".cardme_config.json")
DEFAULT_DATA_DIR = os.path.join(os.path.expanduser("~"), "CardMe_Data")


# ──────────────────────────────────────────────────────────────
# KONFIGURATION LADEN / SPEICHERN
# ──────────────────────────────────────────────────────────────
def load_config() -> dict:
    """Lädt die App-Konfiguration (Datenpfad usw.) aus dem Home-Verzeichnis."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"data_dir": DEFAULT_DATA_DIR}


def save_config(cfg: dict) -> None:
    """Speichert die App-Konfiguration."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


# ──────────────────────────────────────────────────────────────
# DECK HILFSFUNKTIONEN
# ──────────────────────────────────────────────────────────────
def deck_path(data_dir: str, deck_name: str) -> str:
    """Gibt den Dateipfad für ein Deck zurück."""
    safe = deck_name.replace("/", "_").replace("\\", "_")
    return os.path.join(data_dir, f"{safe}.json")


def list_decks(data_dir: str) -> list[str]:
    """Gibt alle vorhandenen Deck-Namen zurück (alphabetisch sortiert)."""
    if not os.path.isdir(data_dir):
        return []
    decks = []
    for fn in os.listdir(data_dir):
        if fn.endswith(".json"):
            decks.append(fn[:-5])
    return sorted(decks)


def load_deck(data_dir: str, deck_name: str) -> list[dict]:
    """Lädt alle Karten eines Decks. Gibt leere Liste zurück wenn nicht vorhanden."""
    path = deck_path(data_dir, deck_name)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_deck(data_dir: str, deck_name: str, cards: list[dict]) -> None:
    """Speichert/Überschreibt ein Deck als JSON-Datei."""
    os.makedirs(data_dir, exist_ok=True)
    with open(deck_path(data_dir, deck_name), "w", encoding="utf-8") as f:
        json.dump(cards, f, ensure_ascii=False, indent=2)


def delete_deck_file(data_dir: str, deck_name: str) -> None:
    """Löscht die JSON-Datei eines Decks."""
    path = deck_path(data_dir, deck_name)
    if os.path.exists(path):
        os.remove(path)


# ──────────────────────────────────────────────────────────────
# HAUPT-APP
# ──────────────────────────────────────────────────────────────
class CardMeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # customtkinter Grundeinstellungen
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(APP_TITLE)
        self.geometry(f"{APP_W}x{APP_H}")
        self.minsize(700, 500)
        self.configure(fg_color=BG)

        # App-Icon setzen (funktioniert sowohl als .py als auch als .exe)
        _base = getattr(__import__('sys'), '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        _icon_path = os.path.join(_base, "img", "icon.ico")
        _icon_png  = os.path.join(_base, "img", "image.png")
        try:
            if os.path.exists(_icon_path):
                self.iconbitmap(_icon_path)
            elif os.path.exists(_icon_png):
                from PIL import Image, ImageTk as _ITk
                _ico = _ITk.PhotoImage(Image.open(_icon_png).resize((48, 48)))
                self.iconphoto(True, _ico)
                self._icon_ref = _ico
        except Exception:
            pass

        self.config    = load_config()
        os.makedirs(self.config["data_dir"], exist_ok=True)

        self.current_deck: str | None = None
        self.deck_cards: list[dict]   = []
        self.learn_index: int         = 0
        self.learn_order: list[int]   = []
        self.answer_visible: bool     = False
        self._flip_animating: bool    = False
        self.CARD_W = 480
        self.CARD_H = 260
        self.FLIP_STEPS = 10

        self._build_ui()
        self._refresh_deck_list()

    # ── Layout ────────────────────────────────────────────────

    def _build_ui(self):
        """Erstellt das Haupt-UI mit Sidebar und Content-Bereich."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ──
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=SIDEBAR_BG, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(2, weight=1)
        self.sidebar.grid_propagate(False)

        # Logo: "Card" weiß + "Me" gelb
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=18, pady=(24, 6), sticky="w")
        ctk.CTkLabel(logo_frame, text="Card",
                     font=ctk.CTkFont(FONT, 26, "bold"), text_color=WHITE).pack(side="left")
        ctk.CTkLabel(logo_frame, text="Me",
                     font=ctk.CTkFont(FONT, 26, "bold"), text_color=YELLOW).pack(side="left")

        ctk.CTkLabel(
            self.sidebar, text="DECKS",
            font=ctk.CTkFont(FONT, 9, "bold"), text_color=TEXT_SEC, anchor="w"
        ).grid(row=1, column=0, padx=18, pady=(10, 2), sticky="w")

        self.deck_list_frame = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent",
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=YELLOW
        )
        self.deck_list_frame.grid(row=2, column=0, padx=8, pady=0, sticky="nsew")
        self.deck_list_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            self.sidebar, text="+ Neues Deck",
            fg_color=YELLOW, hover_color=YELLOW_HVR,
            text_color="#FFFFFF",
            font=ctk.CTkFont(FONT, 12, "bold"), height=34,
            command=self._prompt_new_deck
        ).grid(row=3, column=0, padx=10, pady=8, sticky="ew")

        ctk.CTkButton(
            self.sidebar, text="⚙  Einstellungen",
            fg_color="transparent", hover_color=CARD_BG,
            text_color=TEXT_SEC, font=ctk.CTkFont(FONT, 11), height=28,
            command=self._open_settings
        ).grid(row=4, column=0, padx=10, pady=(0, 14), sticky="ew")

        # ── Content-Bereich ──
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.grid(row=0, column=1, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(2, weight=1)

        self.tab_bar = ctk.CTkFrame(self.content, fg_color=SIDEBAR_BG, height=48, corner_radius=0)
        self.tab_bar.grid(row=0, column=0, sticky="ew")

        self.tab_btns: dict[str, ctk.CTkButton] = {}
        for i, (key, label) in enumerate([
            ("learn",  "Lernen"),
            ("add",    "Karte hinzufügen"),
            ("manage", "Karten verwalten"),
        ]):
            btn = ctk.CTkButton(
                self.tab_bar, text=label, fg_color="transparent",
                hover_color=CARD_BG, text_color=TEXT_SEC,
                font=ctk.CTkFont(FONT, 12), height=48, corner_radius=0,
                command=lambda k=key: self._switch_tab(k)
            )
            btn.grid(row=0, column=i, padx=0, pady=0)
            self.tab_btns[key] = btn

        # ── Aktives-Deck-Banner ──
        self.deck_banner = ctk.CTkFrame(
            self.content, fg_color=CARD_BG, height=36, corner_radius=0
        )
        self.deck_banner.grid(row=1, column=0, sticky="ew")
        self.deck_banner.grid_columnconfigure(0, weight=1)
        self.deck_banner.grid_propagate(False)

        self.lbl_deck_banner = ctk.CTkLabel(
            self.deck_banner,
            text="Kein Deck ausgewählt  –  wähle eines in der Seitenleiste",
            font=ctk.CTkFont(FONT, 11),
            text_color=TEXT_SEC,
            anchor="center",
        )
        self.lbl_deck_banner.grid(row=0, column=0, sticky="ew", padx=16, pady=0)

        self.tab_content = ctk.CTkFrame(self.content, fg_color=BG, corner_radius=0)
        self.tab_content.grid(row=2, column=0, sticky="nsew")
        self.tab_content.grid_columnconfigure(0, weight=1)
        self.tab_content.grid_rowconfigure(0, weight=1)

        self.frames: dict[str, ctk.CTkFrame] = {}
        self._build_learn_tab()
        self._build_add_tab()
        self._build_manage_tab()
        self._switch_tab("learn")

    # ── Tab-Navigation ─────────────────────────────────────────

    def _switch_tab(self, key: str):
        """Aktiviert den gewählten Tab und hebt ihn hervor."""
        for k, btn in self.tab_btns.items():
            if k == key:
                btn.configure(text_color=BLUE, fg_color=BG)
            else:
                btn.configure(text_color=TEXT_SEC, fg_color="transparent")

        for k, frame in self.frames.items():
            if k == key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

        if key == "learn":
            self._reset_learn()
        elif key == "manage":
            self._refresh_manage_tab()

    # ── LEARN-Tab ──────────────────────────────────────────────

    def _build_learn_tab(self):
        """Baut den Lernmodus-Tab mit Flip-Animation auf."""
        frame = ctk.CTkFrame(self.tab_content, fg_color=BG, corner_radius=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self.frames["learn"] = frame

        outer = ctk.CTkFrame(frame, fg_color="transparent")
        outer.grid(row=0, column=0)

        self.lbl_progress = ctk.CTkLabel(
            outer, text="",
            font=ctk.CTkFont(FONT, 11), text_color=TEXT_SEC
        )
        self.lbl_progress.pack(pady=(0, 12))

        # Karten-Frame (Breite wird für Flip-Animation skaliert)
        self.card_outer = ctk.CTkFrame(outer, fg_color="transparent")
        self.card_outer.pack()

        self.card_frame = ctk.CTkFrame(
            self.card_outer,
            width=self.CARD_W, height=self.CARD_H,
            fg_color=CARD_BG, corner_radius=20,
            border_width=2, border_color=BORDER
        )
        self.card_frame.pack()
        self.card_frame.pack_propagate(False)

        self.lbl_side_hint = ctk.CTkLabel(
            self.card_frame, text="",
            font=ctk.CTkFont(FONT, 9, "bold"), text_color=YELLOW
        )
        self.lbl_side_hint.place(relx=0.5, rely=0.13, anchor="center")

        self.lbl_front = ctk.CTkLabel(
            self.card_frame,
            text="Wähle zuerst ein Deck aus.",
            font=ctk.CTkFont(FONT, 19, "bold"),
            text_color=WHITE, wraplength=420
        )
        self.lbl_front.place(relx=0.5, rely=0.44, anchor="center")

        self.lbl_back = ctk.CTkLabel(
            self.card_frame, text="",
            font=ctk.CTkFont(FONT, 15),
            text_color=WHITE, wraplength=420
        )
        self.lbl_back.place(relx=0.5, rely=0.76, anchor="center")

        self.divider_canvas = tk.Canvas(
            self.card_frame, height=1, bg=BORDER,
            highlightthickness=0, bd=0
        )

        # Buttons
        btn_row = ctk.CTkFrame(outer, fg_color="transparent")
        btn_row.pack(pady=18)

        self.btn_reveal = ctk.CTkButton(
            btn_row, text="Antwort aufdecken",
            fg_color=YELLOW, hover_color=YELLOW_HVR,
            text_color="#FFFFFF",
            font=ctk.CTkFont(FONT, 13, "bold"), width=210, height=42,
            command=self._reveal_answer
        )
        self.btn_reveal.pack(side="left", padx=6)

        self.btn_next = ctk.CTkButton(
            btn_row, text="Nächste Karte  →",
            fg_color=CARD_BG, hover_color=BORDER,
            text_color=WHITE,
            font=ctk.CTkFont(FONT, 13), width=170, height=42,
            command=self._next_card
        )
        self.btn_next.pack(side="left", padx=6)

        self.btn_shuffle = ctk.CTkButton(
            outer, text="↺  Neu mischen",
            fg_color="transparent", hover_color=CARD_BG,
            text_color=TEXT_SEC, font=ctk.CTkFont(FONT, 11), height=28,
            command=self._reset_learn
        )
        self.btn_shuffle.pack()

    def _reset_learn(self):
        """Setzt Lernmodus zurück und mischt Karten neu."""
        self._flip_animating = False
        if not self.current_deck or not self.deck_cards:
            msg = "Wähle zuerst ein Deck aus." if not self.current_deck else "Dieses Deck ist noch leer."
            self.lbl_front.configure(text=msg, text_color=WHITE)
            self.lbl_side_hint.configure(text="")
            self.lbl_back.configure(text="")
            self.lbl_progress.configure(text="")
            self.divider_canvas.place_forget()
            self.btn_reveal.configure(state="disabled")
            self.btn_next.configure(state="disabled")
            self.card_frame.configure(width=self.CARD_W, fg_color=CARD_BG, border_color=BORDER)
            return

        self.learn_order = list(range(len(self.deck_cards)))
        random.shuffle(self.learn_order)
        self.learn_index  = 0
        self.answer_visible = False
        self.btn_reveal.configure(state="normal")
        self.btn_next.configure(state="normal")
        self.card_frame.configure(width=self.CARD_W, fg_color=CARD_BG, border_color=BORDER)
        self._show_card_front()

    def _show_card_front(self):
        """Zeigt die Vorderseite der aktuellen Karte."""
        if self.learn_index >= len(self.learn_order):
            self.lbl_front.configure(text="🎉  Alle Karten geschafft!", text_color=YELLOW)
            self.lbl_side_hint.configure(text="")
            self.lbl_back.configure(text="Deck neu mischen zum Wiederholen.")
            self.lbl_progress.configure(text="")
            self.divider_canvas.place_forget()
            return
        card  = self.deck_cards[self.learn_order[self.learn_index]]
        total = len(self.learn_order)
        self.lbl_progress.configure(text=f"Karte  {self.learn_index + 1}  /  {total}")
        self.lbl_side_hint.configure(text="V O R D E R S E I T E", text_color=YELLOW)
        self.lbl_front.configure(text=card.get("front", ""), text_color=WHITE)
        self.lbl_back.configure(text="")
        self.divider_canvas.place_forget()
        self.answer_visible = False

    def _reveal_answer(self):
        """Startet die Flip-Animation zur Antwort."""
        if self.learn_index >= len(self.learn_order) or self._flip_animating:
            return
        card = self.deck_cards[self.learn_order[self.learn_index]]
        self._flip_to_back(card.get("back", ""))

    def _next_card(self):
        """Nächste Karte – mit Flip-Rückkehr zur Vorderseite."""
        if self._flip_animating:
            return
        self.learn_index += 1
        if self.answer_visible:
            self._flip_to_front()
        else:
            self._show_card_front()

    # ── FLIP-ANIMATION ─────────────────────────────────────────

    def _flip_to_back(self, back_text: str):
        """Animiert Karte zur Rückseite."""
        self._flip_animating = True
        self.btn_reveal.configure(state="disabled")

        def _squeeze(step):
            w = int(self.CARD_W * (1 - step / self.FLIP_STEPS))
            self.card_frame.configure(width=max(w, 4))
            if step < self.FLIP_STEPS:
                self.after(18, lambda: _squeeze(step + 1))
            else:
                self.card_frame.configure(fg_color="#1A2E3A", border_color=BLUE)
                self.lbl_side_hint.configure(text="R Ü C K S E I T E", text_color=YELLOW)
                self.lbl_front.configure(text="", text_color=WHITE)
                self.lbl_back.configure(text=back_text, text_color=WHITE)
                self.divider_canvas.place(relx=0.05, rely=0.56, relwidth=0.9, anchor="w")
                _expand(0)

        def _expand(step):
            w = int(self.CARD_W * step / self.FLIP_STEPS)
            self.card_frame.configure(width=max(w, 4))
            if step < self.FLIP_STEPS:
                self.after(18, lambda: _expand(step + 1))
            else:
                self.card_frame.configure(width=self.CARD_W)
                self._flip_animating = False
                self.answer_visible = True

        _squeeze(0)

    def _flip_to_front(self):
        """Animiert Karte zurück zur Vorderseite."""
        self._flip_animating = True

        def _squeeze(step):
            w = int(self.CARD_W * (1 - step / self.FLIP_STEPS))
            self.card_frame.configure(width=max(w, 4))
            if step < self.FLIP_STEPS:
                self.after(18, lambda: _squeeze(step + 1))
            else:
                self.card_frame.configure(fg_color=CARD_BG, border_color=BORDER)
                self._show_card_front()
                _expand(0)

        def _expand(step):
            w = int(self.CARD_W * step / self.FLIP_STEPS)
            self.card_frame.configure(width=max(w, 4))
            if step < self.FLIP_STEPS:
                self.after(18, lambda: _expand(step + 1))
            else:
                self.card_frame.configure(width=self.CARD_W)
                self._flip_animating = False
                self.btn_reveal.configure(state="normal")

        _squeeze(0)

    # ── ADD-Tab ────────────────────────────────────────────────

    def _build_add_tab(self):
        """Tab zum Hinzufügen neuer Karten."""
        frame = ctk.CTkFrame(self.tab_content, fg_color=BG, corner_radius=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        self.frames["add"] = frame

        box = ctk.CTkFrame(frame, fg_color=CARD_BG, corner_radius=16,
                           border_width=1, border_color=BORDER)
        box.grid(row=0, column=0, padx=70, pady=36, sticky="n")
        box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            box, text="Neue Karte erstellen",
            font=ctk.CTkFont(FONT, 17, "bold"), text_color=WHITE
        ).grid(row=0, column=0, padx=28, pady=(24, 16))

        ctk.CTkLabel(box, text="Vorderseite",
                     font=ctk.CTkFont(FONT, 11, "bold"), text_color=YELLOW
                     ).grid(row=1, column=0, padx=28, sticky="w")
        self.entry_front = ctk.CTkTextbox(
            box, width=380, height=90, fg_color=SURFACE2,
            font=ctk.CTkFont(FONT, 13), border_width=1, border_color=BORDER,
            text_color=WHITE
        )
        self.entry_front.grid(row=2, column=0, padx=28, pady=(2, 14))

        ctk.CTkLabel(box, text="Rückseite",
                     font=ctk.CTkFont(FONT, 11, "bold"), text_color=YELLOW
                     ).grid(row=3, column=0, padx=28, sticky="w")
        self.entry_back = ctk.CTkTextbox(
            box, width=380, height=90, fg_color=SURFACE2,
            font=ctk.CTkFont(FONT, 13), border_width=1, border_color=BORDER,
            text_color=WHITE
        )
        self.entry_back.grid(row=4, column=0, padx=28, pady=(2, 14))

        self.lbl_add_status = ctk.CTkLabel(
            box, text="", font=ctk.CTkFont(FONT, 11), text_color=YELLOW
        )
        self.lbl_add_status.grid(row=5, column=0, pady=(0, 6))

        ctk.CTkButton(
            box, text="Karte speichern",
            fg_color=YELLOW, hover_color=YELLOW_HVR,
            text_color="#FFFFFF",
            font=ctk.CTkFont(FONT, 13, "bold"), height=40, width=210,
            command=self._save_card
        ).grid(row=6, column=0, padx=28, pady=(0, 24))

    def _save_card(self):
        """Speichert eine neue Karte im aktuell ausgewählten Deck."""
        if not self.current_deck:
            messagebox.showwarning("Kein Deck", "Bitte wähle zuerst ein Deck in der Seitenleiste aus.")
            return

        front = self.entry_front.get("1.0", "end").strip()
        back  = self.entry_back.get("1.0", "end").strip()

        if not front or not back:
            self.lbl_add_status.configure(text="Bitte beide Felder ausfüllen.", text_color="#F87171")
            return

        self.deck_cards.append({"front": front, "back": back})
        save_deck(self.config["data_dir"], self.current_deck, self.deck_cards)

        self.entry_front.delete("1.0", "end")
        self.entry_back.delete("1.0", "end")
        self.lbl_add_status.configure(
            text=f"✓ Gespeichert!  ({len(self.deck_cards)} Karten im Deck)",
            text_color=YELLOW
        )

    # ── MANAGE-Tab ─────────────────────────────────────────────

    def _build_manage_tab(self):
        """Tab zum Verwalten (Bearbeiten & Löschen) aller Karten."""
        frame = ctk.CTkFrame(self.tab_content, fg_color=BG, corner_radius=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        self.frames["manage"] = frame

        self.lbl_manage_title = ctk.CTkLabel(
            frame, text="Karten verwalten",
            font=ctk.CTkFont(FONT, 15, "bold"), text_color=WHITE
        )
        self.lbl_manage_title.grid(row=0, column=0, padx=20, pady=(16, 6), sticky="w")

        self.manage_scroll = ctk.CTkScrollableFrame(
            frame, fg_color=SURFACE2, corner_radius=12,
            scrollbar_button_color=BORDER, scrollbar_button_hover_color=YELLOW
        )
        self.manage_scroll.grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
        self.manage_scroll.grid_columnconfigure(0, weight=1)

    def _refresh_manage_tab(self):
        """Aktualisiert die Kartenliste im Verwaltungs-Tab."""
        for w in self.manage_scroll.winfo_children():
            w.destroy()

        if not self.current_deck:
            ctk.CTkLabel(self.manage_scroll, text="Kein Deck ausgewählt.",
                         text_color=TEXT_SEC, font=ctk.CTkFont(FONT, 12)
                         ).grid(pady=24)
            return

        self.lbl_manage_title.configure(
            text=f"Karten in  »{self.current_deck}«  –  {len(self.deck_cards)} Karten"
        )

        if not self.deck_cards:
            ctk.CTkLabel(self.manage_scroll,
                         text="Dieses Deck enthält noch keine Karten.",
                         text_color=TEXT_SEC, font=ctk.CTkFont(FONT, 12)
                         ).grid(pady=24)
            return

        for idx, card in enumerate(self.deck_cards):
            row = ctk.CTkFrame(self.manage_scroll, fg_color=CARD_BG,
                               corner_radius=10, border_width=1, border_color=BORDER)
            row.grid(row=idx, column=0, padx=6, pady=4, sticky="ew")
            row.grid_columnconfigure(0, weight=1)

            preview = f"V:  {card.get('front','')[:72]}   │   R:  {card.get('back','')[:72]}"
            ctk.CTkLabel(
                row, text=preview,
                font=ctk.CTkFont(FONT, 11), text_color=TEXT_PRI,
                anchor="w", wraplength=500
            ).grid(row=0, column=0, padx=14, pady=10, sticky="ew")

            btn_box = ctk.CTkFrame(row, fg_color="transparent")
            btn_box.grid(row=0, column=1, padx=6, pady=4)

            ctk.CTkButton(
                btn_box, text="✎  Bearbeiten", width=110, height=30,
                fg_color=YELLOW, hover_color=YELLOW_HVR,
                text_color="#FFFFFF", font=ctk.CTkFont(FONT, 11, "bold"),
                command=lambda i=idx: self._edit_card(i)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                btn_box, text="✕", width=30, height=30,
                fg_color="transparent", hover_color="#3B1A1A",
                text_color="#F87171", font=ctk.CTkFont(FONT, 13, "bold"),
                command=lambda i=idx: self._delete_card(i)
            ).pack(side="left")

    def _delete_card(self, idx: int):
        """Löscht eine Karte nach Bestätigung."""
        card = self.deck_cards[idx]
        if messagebox.askyesno("Karte löschen",
                               f"Karte wirklich löschen?\n\nV: {card.get('front','')}\nR: {card.get('back','')}"):
            self.deck_cards.pop(idx)
            save_deck(self.config["data_dir"], self.current_deck, self.deck_cards)
            self._refresh_manage_tab()

    def _edit_card(self, idx: int):
        """Öffnet Dialog zum Bearbeiten einer bestehenden Karte."""
        card = self.deck_cards[idx]

        win = ctk.CTkToplevel(self)
        win.title("Karte bearbeiten")
        win.geometry("520x380")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.grab_set()

        ctk.CTkLabel(win, text="Karte bearbeiten",
                     font=ctk.CTkFont(FONT, 16, "bold"), text_color=WHITE
                     ).pack(padx=28, pady=(22, 14), anchor="w")

        ctk.CTkLabel(win, text="Vorderseite",
                     font=ctk.CTkFont(FONT, 11, "bold"), text_color=YELLOW
                     ).pack(padx=28, anchor="w")
        txt_front = ctk.CTkTextbox(
            win, width=460, height=90, fg_color=SURFACE2,
            font=ctk.CTkFont(FONT, 13), border_width=1, border_color=BORDER,
            text_color=WHITE
        )
        txt_front.pack(padx=28, pady=(2, 12))
        txt_front.insert("1.0", card.get("front", ""))

        ctk.CTkLabel(win, text="Rückseite",
                     font=ctk.CTkFont(FONT, 11, "bold"), text_color=YELLOW
                     ).pack(padx=28, anchor="w")
        txt_back = ctk.CTkTextbox(
            win, width=460, height=90, fg_color=SURFACE2,
            font=ctk.CTkFont(FONT, 13), border_width=1, border_color=BORDER,
            text_color=WHITE
        )
        txt_back.pack(padx=28, pady=(2, 12))
        txt_back.insert("1.0", card.get("back", ""))

        lbl_status = ctk.CTkLabel(win, text="", font=ctk.CTkFont(FONT, 11), text_color=YELLOW)
        lbl_status.pack()

        def _apply():
            new_front = txt_front.get("1.0", "end").strip()
            new_back  = txt_back.get("1.0", "end").strip()
            if not new_front or not new_back:
                lbl_status.configure(text="Beide Felder müssen ausgefüllt sein.", text_color="#F87171")
                return
            self.deck_cards[idx] = {"front": new_front, "back": new_back}
            save_deck(self.config["data_dir"], self.current_deck, self.deck_cards)
            win.destroy()
            self._refresh_manage_tab()

        ctk.CTkButton(
            win, text="Änderungen speichern",
            fg_color=YELLOW, hover_color=YELLOW_HVR,
            text_color="#FFFFFF",
            font=ctk.CTkFont(FONT, 13, "bold"), height=38, width=220,
            command=_apply
        ).pack(pady=10)

    # ── SIDEBAR / DECK-MANAGEMENT ──────────────────────────────

    def _refresh_deck_list(self):
        """Aktualisiert die Deck-Liste in der Sidebar."""
        for w in self.deck_list_frame.winfo_children():
            w.destroy()

        decks = list_decks(self.config["data_dir"])
        if not decks:
            ctk.CTkLabel(
                self.deck_list_frame,
                text="Noch keine Decks.\nErstelle eines →",
                font=ctk.CTkFont(FONT, 10), text_color=TEXT_SEC, justify="left"
            ).pack(anchor="w", padx=6, pady=10)
            return

        for deck in decks:
            active = (deck == self.current_deck)
            btn = ctk.CTkButton(
                self.deck_list_frame,
                text=f"  {deck}",
                fg_color=YELLOW if active else "transparent",
                hover_color=YELLOW_HVR if active else CARD_BG,
                text_color="#FFFFFF" if active else TEXT_SEC,
                font=ctk.CTkFont(FONT, 12, "bold" if active else "normal"),
                height=34, anchor="w",
                command=lambda d=deck: self._select_deck(d)
            )
            btn.pack(fill="x", pady=2)

            ctx = tk.Menu(self, tearoff=0, bg=CARD_BG, fg=WHITE,
                          activebackground=YELLOW, activeforeground="#FFFFFF",
                          border=0, relief="flat")
            ctx.add_command(label="Deck löschen", command=lambda d=deck: self._delete_deck(d))
            btn.bind("<Button-3>", lambda e, m=ctx: m.tk_popup(e.x_root, e.y_root))

    def _update_deck_banner(self):
        """Aktualisiert den Deck-Anzeige-Banner in der Mitte."""
        if self.current_deck:
            self.lbl_deck_banner.configure(
                text=f"📂  Aktives Deck:   {self.current_deck}   ·   {len(self.deck_cards)} Karten",
                text_color=YELLOW
            )
        else:
            self.lbl_deck_banner.configure(
                text="Kein Deck ausgewählt  –  wähle eines in der Seitenleiste",
                text_color=TEXT_SEC
            )

    def _select_deck(self, deck_name: str):
        """Wählt ein Deck aus und lädt seine Karten."""
        self.current_deck = deck_name
        self.deck_cards   = load_deck(self.config["data_dir"], deck_name)
        self._update_deck_banner()
        self._refresh_deck_list()
        self._reset_learn()
        for k, f in self.frames.items():
            if f.winfo_ismapped() and k == "manage":
                self._refresh_manage_tab()
                break

    def _prompt_new_deck(self):
        """Öffnet einen Dialog zur Eingabe des Deck-Namens."""
        dialog = ctk.CTkInputDialog(
            text="Name des neuen Decks:",
            title="Neues Deck erstellen"
        )
        name = dialog.get_input()
        if name and name.strip():
            name = name.strip()
            if name in list_decks(self.config["data_dir"]):
                messagebox.showinfo("Bereits vorhanden", f"Das Deck »{name}« existiert bereits.")
                return
            save_deck(self.config["data_dir"], name, [])
            self._select_deck(name)
        elif name is not None:
            messagebox.showwarning("Ungültig", "Der Deck-Name darf nicht leer sein.")

    def _delete_deck(self, deck_name: str):
        """Löscht ein Deck nach Bestätigung."""
        count = len(load_deck(self.config["data_dir"], deck_name))
        if messagebox.askyesno("Deck löschen",
                               f"Deck »{deck_name}« mit {count} Karten wirklich löschen?\nDiese Aktion kann nicht rückgängig gemacht werden."):
            delete_deck_file(self.config["data_dir"], deck_name)
            if self.current_deck == deck_name:
                self.current_deck = None
                self.deck_cards   = []
            self._update_deck_banner()
            self._refresh_deck_list()
            self._reset_learn()

    # ── EINSTELLUNGEN ──────────────────────────────────────────

    def _open_settings(self):
        """Einstellungsfenster (Datenpfad ändern)."""
        win = ctk.CTkToplevel(self)
        win.title("Einstellungen")
        win.geometry("500x230")
        win.resizable(False, False)
        win.configure(fg_color=BG)
        win.grab_set()

        ctk.CTkLabel(win, text="Einstellungen",
                     font=ctk.CTkFont(FONT, 16, "bold"), text_color=WHITE
                     ).pack(padx=24, pady=(22, 10), anchor="w")
        ctk.CTkLabel(win, text="Daten-Ordner (Decks als .json)",
                     font=ctk.CTkFont(FONT, 11), text_color=TEXT_SEC
                     ).pack(padx=24, anchor="w")

        row = ctk.CTkFrame(win, fg_color="transparent")
        row.pack(padx=24, pady=8, fill="x")

        path_var   = tk.StringVar(value=self.config["data_dir"])
        path_entry = ctk.CTkEntry(row, textvariable=path_var, width=330, height=36,
                                  fg_color=SURFACE2, text_color=WHITE, border_color=BORDER)
        path_entry.pack(side="left", padx=(0, 8))

        def browse():
            folder = filedialog.askdirectory(initialdir=path_var.get(), title="Ordner wählen")
            if folder:
                path_var.set(folder)

        ctk.CTkButton(row, text="Durchsuchen", width=100, height=36,
                      fg_color=YELLOW, hover_color=YELLOW_HVR,
                      text_color="#FFFFFF", command=browse).pack(side="left")

        def apply_settings():
            new_dir = path_var.get().strip()
            if not new_dir:
                messagebox.showwarning("Ungültig", "Pfad darf nicht leer sein.", parent=win)
                return
            old_dir = self.config["data_dir"]
            if new_dir != old_dir:
                try:
                    os.makedirs(new_dir, exist_ok=True)
                    existing = [f for f in os.listdir(old_dir) if f.endswith(".json")] if os.path.isdir(old_dir) else []
                    if existing and messagebox.askyesno("Dateien kopieren",
                                                        f"{len(existing)} Deck-Datei(en) kopieren?", parent=win):
                        for fn in existing:
                            shutil.copy2(os.path.join(old_dir, fn), os.path.join(new_dir, fn))
                except Exception as e:
                    messagebox.showerror("Fehler", str(e), parent=win)
                    return
                self.config["data_dir"] = new_dir
                save_config(self.config)
                self._refresh_deck_list()
            win.destroy()
            messagebox.showinfo("Gespeichert", "Einstellungen gespeichert.")

        ctk.CTkButton(win, text="Speichern & Schließen",
                      fg_color=YELLOW, hover_color=YELLOW_HVR,
                      text_color="#FFFFFF",
                      font=ctk.CTkFont(FONT, 13, "bold"), height=38,
                      command=apply_settings).pack(pady=14)


# ──────────────────────────────────────────────────────────────
# EINSTIEGSPUNKT
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = CardMeApp()
    app.mainloop()
