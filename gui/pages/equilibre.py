"""Bonus 2 : ABR équilibré (milieu d'abord, inserer_abr) vs ABR classique sur moyennes croissantes."""
import random
import tkinter as tk
from tkinter import ttk
import theme as T
import frames as F
import graphes as G
from widgets import Lecteur, VueArbre, VueTableau


class PageEquilibre(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app, self.b = app, app.b
        ttk.Label(self, text="Bonus 2 – ABR équilibré vs ABR classique", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="À partir des moyennes triées : 1) trouver le milieu ; 2) l'insérer avec inserer_abr() ; "
                             "3) traiter récursivement la moitié gauche ; 4) puis la moitié droite. "
                             "Comparé à l'ABR classique obtenu en insérant les moyennes dans l'ordre croissant "
                             "(pire cas : peigne de hauteur n).", style="Muet.TLabel", wraplength=1100).pack(anchor="w", pady=(0, 8))
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)

        # --- côte à côte + animation ---
        a = ttk.Frame(nb, padding=8)
        nb.add(a, text="Construction et visualisation")
        barre = ttk.Frame(a, style="Carte.TFrame", padding=8)
        barre.pack(fill="x")
        ttk.Label(barre, text="n (≤ 63 pour le dessin)", style="Carte.TLabel").pack(side="left")
        self.n = ttk.Spinbox(barre, from_=3, to=63, width=4)
        self.n.set(15)
        self.n.pack(side="left", padx=4)
        ttk.Button(barre, text="Construire les deux arbres (C)", style="Accent.TButton", command=self.construire).pack(side="left", padx=4)
        ttk.Button(barre, text="Animer la construction équilibrée", command=lambda: self.animer(True)).pack(side="left", padx=4)
        ttk.Button(barre, text="Animer la construction classique", command=lambda: self.animer(False)).pack(side="left", padx=4)
        self.info = ttk.Label(barre, text="", style="Carte.TLabel", font=T.MONO)
        self.info.pack(side="left", padx=10)
        deux = ttk.Frame(a)
        deux.pack(fill="both", expand=True, pady=6)
        g = T.carte(deux, "ABR classique (insertions croissantes)")
        g.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self.v_classique = VueArbre(g, hauteur=230, prof_max=64)
        self.v_classique.pack(fill="both", expand=True)
        d = T.carte(deux, "ABR équilibré (milieu d'abord)")
        d.pack(side="left", fill="both", expand=True, padx=(4, 0))
        self.v_equi = VueArbre(d, hauteur=230)
        self.v_equi.pack(fill="both", expand=True)
        anim = T.carte(a, "Animation pas à pas (trace C)")
        anim.pack(fill="both", expand=True)
        self.v_tab = VueTableau(anim, hauteur=90, mode="cases")
        self.v_tab.pack(fill="x")
        self.v_anim = VueArbre(anim, hauteur=220)
        self.v_anim.pack(fill="both", expand=True)
        self.msg = ttk.Label(anim, text="", style="CarteSous.TLabel")
        self.msg.pack(anchor="w")
        self.lecteur = Lecteur(anim, self._rendu, lambda m: self.msg.config(text=m))
        self.lecteur.pack(fill="x")

        # --- mesures ---
        c = ttk.Frame(nb, padding=8)
        nb.add(c, text="Temps et hauteurs")
        haut = ttk.Frame(c, style="Carte.TFrame", padding=8)
        haut.pack(fill="x")
        ttk.Label(haut, text="Mesure immédiate en C, n =", style="Carte.TLabel").pack(side="left")
        self.nm = ttk.Spinbox(haut, from_=100, to=30000, width=7)
        self.nm.set(5000)
        self.nm.pack(side="left", padx=4)
        ttk.Button(haut, text="Mesurer", command=self.mesurer).pack(side="left")
        self.res = ttk.Label(haut, text="", style="Carte.TLabel", font=T.MONO)
        self.res.pack(side="left", padx=10)
        cadre = ttk.Frame(c)
        cadre.pack(fill="both", expand=True, pady=6)
        self.toile = G.Toile(cadre, 11, 5)
        f = self.toile.fig
        ax1, ax2, ax3 = f.add_subplot(131), f.add_subplot(132), f.add_subplot(133)
        G.tracer_serie(ax1, "construction", [("S3_croissant", "Classique (croissant)", "n2"),
                                             ("S3_equilibre", "Équilibré", "nlogn")], logy=True)
        ax1.set_title("Temps de construction")
        G.tracer_serie(ax2, "recherche", [("S3_degenere_moyen", "Classique dégénéré", "n"),
                                          ("S3_equilibre_moyen", "Équilibré", "logn")], logy=True)
        ax2.set_title("Recherche (moyenne existante)")
        G.tracer_serie(ax3, "hauteur", [("S3_croissant", "Classique", "n"), ("S3_equilibre", "Équilibré", None),
                                        ("log2_n", "log2(n)", None)], logy=True, theorie=False)
        ax3.set_title("Hauteur")
        self.toile.dessiner()

    def _valeurs(self):
        try:
            n = max(3, min(63, int(self.n.get())))
        except ValueError:
            n = 15
        return sorted(random.randint(200, 1950) for _ in range(n))

    def construire(self):
        v = self._valeurs()
        self.cles = v
        self.b.anim_abr_sequence(v, False)
        hc = self.b.anim_abr_hauteur()
        mod, rac = F.modele_depuis_export(self.b.anim_abr_exporter())
        self.v_classique.dessiner(dict(mod=mod, rac=rac, roles={}))
        self.b.anim_abr_sequence(v, True)
        he = self.b.anim_abr_hauteur()
        mod, rac = F.modele_depuis_export(self.b.anim_abr_exporter())
        self.v_equi.dessiner(dict(mod=mod, rac=rac, roles={}))
        self.info.config(text=f"n = {len(v)} : hauteur classique = {hc}, hauteur équilibré = {he}")

    def animer(self, equilibre):
        v = getattr(self, "cles", None) or self._valeurs()
        self.cles = v
        evs = self.b.anim_abr_sequence(v, equilibre)
        apres = self.b.anim_abr_exporter()
        imgs = F.frames_arbre(None, evs, apres, titre="Arbre vide", tableau=sorted(v))
        imgs[-1]["msg"] = f"Hauteur obtenue : {self.b.anim_abr_hauteur()}"
        self.lecteur.charger(imgs)

    def _rendu(self, img):
        self.v_anim.dessiner(img)
        tab = img.get("tableau") or []
        rng = img.get("rng")
        roles = {}
        if rng:
            roles = {i: T.C_HORS for i in range(len(tab)) if not rng[0] <= i <= rng[2]}
            roles[rng[1]] = T.C_PIVOT
        self.v_tab.dessiner(dict(arr=tab, roles=roles))

    def mesurer(self):
        try:
            n = int(self.nm.get())
        except ValueError:
            n = 5000
        r = self.b.bench_abr(n)
        self.res.config(text=f"classique : {r['t_classique']:.3f} ms, hauteur {r['h_classique']}   |   "
                             f"équilibré : {r['t_equilibre']:.3f} ms, hauteur {r['h_equilibre']}")
