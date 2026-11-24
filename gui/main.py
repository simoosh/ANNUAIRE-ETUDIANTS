"""
main.py — Interface graphique du Mini-projet A (Gestionnaire d'annuaire d'étudiants).

Lancement :  python gui/main.py      (après compilation : build.bat ou mingw32-make)

Architecture :
  backend.py  liaison ctypes avec la bibliothèque C (TOUS les algorithmes sont en C)
  frames.py   rejoue la trace d'exécution C pour produire les étapes d'animation
  widgets.py  lecteur d'animation, vues tableau / liste / arbre / tas
  data.py     lecture des CSV produits par le benchmark C
  pages/      les 11 sections de la barre latérale
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import theme as T                                   # noqa: E402
from backend import Backend, BackendErreur          # noqa: E402
from pages.dashboard import PageTableauDeBord       # noqa: E402
from pages.etudiants import PageEtudiants           # noqa: E402
from pages.structures import PageS1, PageS2, PageS3  # noqa: E402
from pages.visualiseur import PageVisualiseur       # noqa: E402
from pages.tas import PageTas                       # noqa: E402
from pages.equilibre import PageEquilibre           # noqa: E402
from pages.experiences import PageExperiences       # noqa: E402
from pages.complexite import PageComplexite         # noqa: E402
from pages.rapports import PageRapports             # noqa: E402

SECTIONS = [
    ("dashboard", "  Tableau de bord", PageTableauDeBord),
    ("etudiants", "  Gestion des étudiants", PageEtudiants),
    ("s1", "  S1 – Liste non triée", PageS1),
    ("s2", "  S2 – Tableau trié", PageS2),
    ("s3", "  S3 – Arbre binaire (ABR)", PageS3),
    ("visu", "  Visualiseur d'algorithmes", PageVisualiseur),
    ("tas", "  Tas max (bonus 1)", PageTas),
    ("equi", "  ABR équilibré (bonus 2)", PageEquilibre),
    ("exp", "  Étude expérimentale", PageExperiences),
    ("cmp", "  Comparaison des complexités", PageComplexite),
    ("rap", "  Rapports et export", PageRapports),
]


def activer_dpi():
    """Rendu net sur les écrans à mise à l'échelle (Windows)."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Annuaire d'étudiants – Comparaison de structures de données (Mini-projet A)")
        self.geometry("1440x900")
        self.minsize(1200, 760)
        if sys.platform.startswith("win"):
            self.state("zoomed")
        T.appliquer(self)
        try:
            self.b = Backend()
        except (BackendErreur, OSError) as e:
            messagebox.showerror("Bibliothèque C", str(e))
            self.destroy()
            raise SystemExit(1)
        self.structure_choisie = 2
        self.derniere_operation = "—"
        self.b.generer(200, 0, 2026)               # base initiale
        self._construire()
        self.protocol("WM_DELETE_WINDOW", self.quitter)
        self.afficher("dashboard")

    def _construire(self):
        barre = tk.Frame(self, bg=T.PANNEAU, width=320)
        barre.pack(side="left", fill="y")
        barre.pack_propagate(False)
        tk.Label(barre, text="ANNUAIRE", bg=T.PANNEAU, fg=T.ACCENT2, font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=18, pady=(18, 0))
        tk.Label(barre, text="Algorithmique et Complexité\nMini-projet A · 2026/2027", bg=T.PANNEAU,
                 fg=T.TEXTE2, font=T.POLICE_P, justify="left").pack(anchor="w", padx=18, pady=(0, 14))
        self.boutons = {}
        for cle, nom, _ in SECTIONS:
            b = tk.Label(barre, text=nom, bg=T.PANNEAU, fg=T.TEXTE, font=("Segoe UI", 10), anchor="w",
                         padx=12, pady=9, cursor="hand2")
            b.pack(fill="x", padx=8, pady=1)
            b.bind("<Button-1>", lambda e, c=cle: self.afficher(c))
            b.bind("<Enter>", lambda e, w=b: w.configure(bg=T.CARTE) if w is not self._actif() else None)
            b.bind("<Leave>", lambda e, w=b: w.configure(bg=T.PANNEAU) if w is not self._actif() else None)
            self.boutons[cle] = b
        tk.Label(barre, text="Université A. Mira de Béjaïa\nDépartement d'Informatique", bg=T.PANNEAU,
                 fg=T.TEXTE2, font=("Segoe UI", 8), justify="left").pack(side="bottom", anchor="w", padx=18, pady=12)

        droite = ttk.Frame(self)
        droite.pack(side="left", fill="both", expand=True)
        self.zone = ttk.Frame(droite, padding=(18, 14))
        self.zone.pack(fill="both", expand=True)
        self.statut = tk.Label(droite, text="", bg=T.PANNEAU, fg=T.TEXTE2, anchor="w", font=T.POLICE_P, padx=12)
        self.statut.pack(fill="x", side="bottom")
        self.pages = {}
        self.courante = None

    def _actif(self):
        return self.boutons.get(self.courante)

    def afficher(self, cle):
        if self.courante in self.pages:
            self.pages[self.courante].pack_forget()
        for c, b in self.boutons.items():
            b.configure(bg=T.CARTE if c == cle else T.PANNEAU, fg=T.ACCENT2 if c == cle else T.TEXTE)
        if cle not in self.pages:
            classe = next(c for k, _, c in SECTIONS if k == cle)
            self.pages[cle] = classe(self.zone, self)
        self.courante = cle
        self.pages[cle].pack(fill="both", expand=True)
        if hasattr(self.pages[cle], "rafraichir"):
            self.pages[cle].rafraichir()
        self.maj_statut()

    def aller(self, cle):
        self.afficher(cle)

    def maj_statut(self, texte=None):
        if texte:
            self.derniere_operation = texte
        self.statut.config(text=f"  Base : {self.b.taille()} étudiants   |   Dernière opération : "
                                f"{self.derniere_operation}   |   Tous les algorithmes sont exécutés en C "
                                f"(build/annuaire.dll)")

    def base_modifiee(self):
        """Appelé après toute modification de la base : les pages se mettront à jour."""
        for p in self.pages.values():
            if hasattr(p, "base_modifiee"):
                p.base_modifiee()
        self.maj_statut()

    def quitter(self):
        self.b.fermer()
        self.destroy()


if __name__ == "__main__":
    activer_dpi()
    Application().mainloop()
