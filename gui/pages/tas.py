"""Bonus 1 : top-k avec un tas max (Entasser, ConstruireTasMax) et comparaison des 4 méthodes."""
import random
import tkinter as tk
from tkinter import ttk
import theme as T
import frames as F
import graphes as G
from widgets import Lecteur, VueTas, legende
from backend import NOMS_STRUCTURES, S1_TABLEAU, S2_TRIE, S3_ABR, TAS


class PageTas(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app, self.b = app, app.b
        ttk.Label(self, text="Bonus 1 – Top-k par tas max", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="Copie des n moyennes de S1, ConstruireTasMax (Θ(n)) puis k extractions du maximum "
                             "(Θ(log n) chacune) : Θ(n + k log n). Comparé au tri rapide de S1, à la lecture "
                             "directe de S2 et à l'infixe inverse de S3.", style="Muet.TLabel",
                  wraplength=1100).pack(anchor="w", pady=(0, 8))
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # ---- animation ----
        a = ttk.Frame(nb, padding=8)
        nb.add(a, text="Animation (Entasser / ConstruireTasMax / extraction)")
        barre = ttk.Frame(a, style="Carte.TFrame", padding=8)
        barre.pack(fill="x")
        ttk.Label(barre, text="n", style="Carte.TLabel").pack(side="left")
        self.n = ttk.Spinbox(barre, from_=3, to=31, width=4)
        self.n.set(15)
        self.n.pack(side="left", padx=4)
        ttk.Label(barre, text="k", style="Carte.TLabel").pack(side="left")
        self.k = ttk.Spinbox(barre, from_=1, to=31, width=4)
        self.k.set(5)
        self.k.pack(side="left", padx=4)
        self.source = ttk.Combobox(barre, values=["valeurs aléatoires", "moyennes de la base (n premiers de S1)"],
                                   state="readonly", width=34)
        self.source.current(0)
        self.source.pack(side="left", padx=6)
        ttk.Button(barre, text="Exécuter en C", style="Accent.TButton", command=self.animer).pack(side="left")
        cv = ttk.Frame(a, style="Carte.TFrame", padding=6)
        cv.pack(fill="both", expand=True, pady=6)
        self.vue = VueTas(cv)
        self.vue.pack(fill="both", expand=True)
        legende(cv, [(T.C_PIVOT, "Entasser(i)"), (T.C_COMPARE, "comparaison père/fils"), (T.C_SWAP, "échange"),
                     (T.C_TRIE, "extrait (hors du tas)")]).pack(anchor="w")
        self.msg = ttk.Label(a, text="", style="Sous.TLabel")
        self.msg.pack(anchor="w")
        self.lecteur = Lecteur(a, self.vue.dessiner, lambda m: self.msg.config(text=m))
        self.lecteur.pack(fill="x")

        # ---- comparaison ----
        c = ttk.Frame(nb, padding=8)
        nb.add(c, text="Comparaison expérimentale des 4 méthodes")
        haut = ttk.Frame(c, style="Carte.TFrame", padding=8)
        haut.pack(fill="x")
        ttk.Label(haut, text="Mesure immédiate sur la base courante (clock() en C), k =", style="Carte.TLabel").pack(side="left")
        self.km = ttk.Spinbox(haut, from_=1, to=100000, width=7)
        self.km.set(10)
        self.km.pack(side="left", padx=4)
        ttk.Button(haut, text="Mesurer", command=self.mesurer).pack(side="left")
        self.res = ttk.Label(haut, text="", style="Carte.TLabel", font=T.MONO)
        self.res.pack(side="left", padx=12)
        cadre = ttk.Frame(c)
        cadre.pack(fill="both", expand=True, pady=6)
        self.toile = G.Toile(cadre, 11, 5)
        self.tracer()

    def tracer(self, mesures=None):
        f = self.toile.fig
        f.clear()
        ax1, ax2, ax3 = f.add_subplot(131), f.add_subplot(132), f.add_subplot(133)
        G.tracer_serie(ax1, "topk", [("S1_tableau_alea", "S1 : tri rapide", "nlogn"), ("Tas_alea", "Tas max", "n"),
                                     ("S3_alea", "S3 : infixe inverse", "logn"), ("S2_alea", "S2 : lecture directe", "1")],
                       logy=True)
        ax1.set_title("Top-k (k = 10) en fonction de n")
        G.tracer_serie(ax2, "topk_k", [("S1_tableau", "S1 : tri rapide", None), ("Tas", "Tas max", None),
                                       ("S3", "S3", None), ("S2", "S2", None)], logy=True, logx=True, xlabel="k")
        ax2.set_title("Top-k en fonction de k (n max)")
        ax3.set_title("Base courante (mesure C)")
        if mesures:
            noms = list(mesures)
            ax3.bar(range(len(noms)), [mesures[x] for x in noms], color=T.SERIES[:len(noms)])
            ax3.set_xticks(range(len(noms)))
            ax3.set_xticklabels(noms, rotation=20, fontsize=7)
            ax3.set_yscale("log")
            ax3.set_ylabel("µs")
        else:
            ax3.text(0.5, 0.5, "cliquer sur « Mesurer »", ha="center", transform=ax3.transAxes, color=T.TEXTE2)
        self.toile.dessiner()

    def mesurer(self):
        try:
            k = int(self.km.get())
        except ValueError:
            k = 10
        if self.b.taille() == 0:
            return
        k = min(k, self.b.taille())
        m = {}
        for meth, nom in [(S1_TABLEAU, "S1 tri rapide"), (TAS, "Tas max"), (S3_ABR, "S3 infixe inv."), (S2_TRIE, "S2 direct")]:
            m[nom] = self.b.mesurer(3, meth, k)[0]
        self.res.config(text="   ".join(f"{a}: {b:.2f} µs" for a, b in m.items()) + f"   (n = {self.b.taille()})")
        self.tracer(m)

    def animer(self):
        try:
            n, k = int(self.n.get()), int(self.k.get())
        except ValueError:
            n, k = 15, 5
        if self.source.current() == 1 and self.b.taille() >= 3:
            v = [e.cle for e in self.b.contenu(S1_TABLEAU)[:n]]
        else:
            v = [random.randint(200, 1950) for _ in range(n)]
        k = min(k, len(v))
        evs, ext = self.b.anim_tas(v, k)
        imgs = F.frames_tableau(v, evs, titre="Copie des moyennes (ordre d'arrivée) avant ConstruireTasMax")
        imgs[-1]["msg"] = f"Les {k} meilleurs (extraits dans l'ordre) : " + ", ".join(f"{x / 100:.2f}" for x in ext)
        self.lecteur.charger(imgs)
