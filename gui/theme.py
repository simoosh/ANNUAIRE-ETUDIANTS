"""theme.py — Thème sombre professionnel (couleurs, polices, styles ttk)."""
import tkinter as tk
from tkinter import ttk

FOND = "#0f1117"
PANNEAU = "#161a23"
CARTE = "#1e2230"
CARTE2 = "#262b3b"
BORDURE = "#2e3446"
TEXTE = "#e6e9ef"
TEXTE2 = "#9aa3b5"
ACCENT = "#4f8cff"
ACCENT2 = "#7aa7ff"

# rôles de surbrillance des animations
C_NORMAL = "#4a5578"
C_COMPARE = "#ffb020"
C_SWAP = "#ff5c5c"
C_SHIFT = "#ff8a3d"
C_PIVOT = "#b06cff"
C_TRIE = "#2ecc71"
C_TROUVE = "#22d3ee"
C_HORS = "#2a3045"
C_INTERVALLE = "#20263a"
C_SUCC = "#e879f9"

SERIES = ["#4f8cff", "#ff5c5c", "#2ecc71", "#ffb020", "#b06cff", "#22d3ee", "#e879f9", "#a3a3a3"]

POLICE = ("Segoe UI", 10)
POLICE_P = ("Segoe UI", 9)
POLICE_G = ("Segoe UI", 11, "bold")
TITRE = ("Segoe UI", 18, "bold")
SOUS_TITRE = ("Segoe UI", 12, "bold")
MONO = ("Consolas", 10)


def appliquer(racine):
    racine.configure(bg=FOND)
    st = ttk.Style(racine)
    st.theme_use("clam")
    st.configure(".", background=FOND, foreground=TEXTE, font=POLICE, fieldbackground=CARTE2,
                 bordercolor=BORDURE, lightcolor=BORDURE, darkcolor=BORDURE)
    st.configure("TFrame", background=FOND)
    st.configure("Carte.TFrame", background=CARTE)
    st.configure("Panneau.TFrame", background=PANNEAU)
    st.configure("TLabel", background=FOND, foreground=TEXTE)
    st.configure("Carte.TLabel", background=CARTE, foreground=TEXTE)
    st.configure("Muet.TLabel", background=FOND, foreground=TEXTE2)
    st.configure("CarteMuet.TLabel", background=CARTE, foreground=TEXTE2, font=POLICE_P)
    st.configure("Titre.TLabel", font=TITRE, background=FOND, foreground=TEXTE)
    st.configure("Sous.TLabel", font=SOUS_TITRE, background=FOND, foreground=TEXTE)
    st.configure("CarteSous.TLabel", font=SOUS_TITRE, background=CARTE, foreground=TEXTE)
    st.configure("Valeur.TLabel", font=("Segoe UI", 20, "bold"), background=CARTE, foreground=ACCENT2)
    st.configure("TButton", background=CARTE2, foreground=TEXTE, padding=(10, 5), borderwidth=0)
    st.map("TButton", background=[("active", BORDURE), ("disabled", PANNEAU)],
           foreground=[("disabled", TEXTE2)])
    st.configure("Accent.TButton", background=ACCENT, foreground="white")
    st.map("Accent.TButton", background=[("active", ACCENT2)])
    st.configure("TEntry", fieldbackground=CARTE2, foreground=TEXTE, insertcolor=TEXTE, padding=4)
    st.configure("TSpinbox", fieldbackground=CARTE2, foreground=TEXTE, arrowcolor=TEXTE, padding=3)
    st.configure("TCombobox", fieldbackground=CARTE2, foreground=TEXTE, arrowcolor=TEXTE, padding=3)
    st.map("TCombobox", fieldbackground=[("readonly", CARTE2)], foreground=[("readonly", TEXTE)])
    racine.option_add("*TCombobox*Listbox.background", CARTE2)
    racine.option_add("*TCombobox*Listbox.foreground", TEXTE)
    st.configure("TRadiobutton", background=FOND, foreground=TEXTE)
    st.configure("Carte.TRadiobutton", background=CARTE, foreground=TEXTE)
    st.map("TRadiobutton", background=[("active", FOND)])
    st.map("Carte.TRadiobutton", background=[("active", CARTE)])
    st.configure("TCheckbutton", background=CARTE, foreground=TEXTE)
    st.map("TCheckbutton", background=[("active", CARTE)])
    st.configure("TNotebook", background=FOND, borderwidth=0)
    st.configure("TNotebook.Tab", background=PANNEAU, foreground=TEXTE2, padding=(14, 6))
    st.map("TNotebook.Tab", background=[("selected", CARTE)], foreground=[("selected", TEXTE)])
    st.configure("Treeview", background=CARTE, fieldbackground=CARTE, foreground=TEXTE,
                 rowheight=24, borderwidth=0)
    st.configure("Treeview.Heading", background=CARTE2, foreground=TEXTE, font=("Segoe UI", 9, "bold"))
    st.map("Treeview", background=[("selected", ACCENT)])
    st.configure("Horizontal.TProgressbar", background=ACCENT, troughcolor=CARTE2)
    st.configure("TScale", background=CARTE)
    st.configure("Vertical.TScrollbar", background=CARTE2, troughcolor=PANNEAU, arrowcolor=TEXTE)
    st.configure("Horizontal.TScrollbar", background=CARTE2, troughcolor=PANNEAU, arrowcolor=TEXTE)
    st.configure("TLabelframe", background=CARTE, bordercolor=BORDURE)
    st.configure("TLabelframe.Label", background=CARTE, foreground=ACCENT2, font=("Segoe UI", 10, "bold"))


def carte(parent, titre=None, grille=False, **kw):
    """Cadre « carte » avec titre optionnel (placé par grid si grille=True)."""
    f = ttk.Frame(parent, style="Carte.TFrame", padding=12, **kw)
    if titre:
        l = ttk.Label(f, text=titre, style="CarteSous.TLabel")
        if grille:
            l.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 6))
        else:
            l.pack(anchor="w", pady=(0, 6))
    return f


def texte(parent, hauteur=8, **kw):
    t = tk.Text(parent, height=hauteur, bg=CARTE2, fg=TEXTE, insertbackground=TEXTE, relief="flat",
                font=MONO, wrap="word", padx=8, pady=6, **kw)
    t.tag_configure("titre", foreground=ACCENT2, font=("Consolas", 10, "bold"))
    t.tag_configure("ok", foreground=C_TRIE)
    t.tag_configure("err", foreground=C_SWAP)
    t.tag_configure("muet", foreground=TEXTE2)
    return t
