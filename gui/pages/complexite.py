"""Tableaux de bord de complexité : un par structure, comparaisons, tableau théorique."""
import tkinter as tk
from tkinter import ttk
import theme as T
import data
import graphes as G


class PageComplexite(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        ttk.Label(self, text="Comparaison des complexités", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="Traits pleins : mesures expérimentales (CSV du benchmark C). Pointillés : complexité "
                             "théorique a·f(n), le coefficient a étant ajusté par moindres carrés sur la même série.",
                  style="Muet.TLabel").pack(anchor="w", pady=(0, 6))
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True)
        self.toiles = {}
        for nom in ["S1", "S2", "S3", "Comparaison"]:
            f = ttk.Frame(self.nb)
            self.nb.add(f, text={"S1": "S1 – liste non triée", "S2": "S2 – tableau trié", "S3": "S3 – ABR",
                                 "Comparaison": "S1 / S2 / S3 ensemble"}[nom])
            self.toiles[nom] = G.Toile(f, 12, 7)
        # tableau théorique
        t = ttk.Frame(self.nb, padding=10)
        self.nb.add(t, text="Complexités théoriques")
        arbre = ttk.Treeview(t, columns=("s1t", "s1l", "s2", "s3"), show="tree headings", height=10)
        arbre.heading("#0", text="Opération (meilleur / moyen / pire)")
        for c, h in zip(("s1t", "s1l", "s2", "s3"), ("S1 tableau", "S1 liste chaînée", "S2 tableau trié", "S3 ABR")):
            arbre.heading(c, text=h)
            arbre.column(c, width=230)
        arbre.column("#0", width=210)
        for op, *v in data.COMPLEXITES:
            arbre.insert("", "end", text=op, values=v)
        arbre.pack(fill="x")
        ttk.Label(t, text="h = hauteur de l'ABR (≈ log n si insertions aléatoires, n si moyennes triées) ; "
                          "d = nombre d'étudiants ayant la moyenne cherchée ; k = paramètre du top-k.\n"
                          "* Θ(1) pour S3 : insertion à la racine d'un arbre vide ; en pratique Θ(h).",
                  style="Muet.TLabel", justify="left").pack(anchor="w", pady=8)
        self.synth = ttk.Treeview(t, columns=("op", "theo", "val", "tend"), show="tree headings", height=14)
        self.synth.heading("#0", text="Structure")
        for c, h, w in (("op", "Opération", 120), ("theo", "Théorie", 110), ("val", "Mesure à n max", 150),
                        ("tend", "Tendance observée (pente log-log)", 260)):
            self.synth.heading(c, text=h)
            self.synth.column(c, width=w)
        self.synth.pack(fill="both", expand=True)
        self.dessine = False

    def rafraichir(self):
        if self.dessine and data.disponible():
            return
        for nom, toile in self.toiles.items():
            f = toile.fig
            f.clear()
            graphes = data.TABLEAUX_DE_BORD[nom]
            for i, (titre, op, series, logy) in enumerate(graphes):
                ax = f.add_subplot(2, 3, i + 1)
                G.tracer_serie(ax, op, series, logy=logy, theorie=(nom != "Comparaison"))
                ax.set_title(titre)
            toile.dessiner()
        self.synth.delete(*self.synth.get_children())
        for nom, op, theo, val, tend, _ in data.tableau_synthese():
            self.synth.insert("", "end", text=nom, values=(op, theo, val, tend))
        self.dessine = data.disponible()
