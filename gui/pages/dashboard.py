"""Tableau de bord : état de la base, structure choisie, dernière expérience, accès rapides."""
import tkinter as tk
from tkinter import ttk
import theme as T
import data
from backend import NOMS_STRUCTURES


class PageTableauDeBord(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app, self.b = app, app.b
        ttk.Label(self, text="Tableau de bord", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="Gestionnaire d'annuaire d'étudiants — comparaison expérimentale de trois "
                             "structures de stockage (S1 liste non triée, S2 tableau trié, S3 ABR).",
                  style="Muet.TLabel").pack(anchor="w", pady=(0, 12))

        cartes = ttk.Frame(self)
        cartes.pack(fill="x")
        self.valeurs = {}
        for i, (cle, titre) in enumerate([("total", "Étudiants dans la base"), ("structure", "Structure sélectionnée"),
                                          ("hauteur", "Hauteur de l'ABR (S3)"), ("memoire", "Mémoire totale"),
                                          ("temps", "Recherche moyenne (n max)"), ("exp", "Dernière expérience")]):
            c = T.carte(cartes)
            c.grid(row=i // 3, column=i % 3, sticky="nsew", padx=6, pady=6)
            ttk.Label(c, text=titre, style="CarteMuet.TLabel").pack(anchor="w")
            v = ttk.Label(c, text="—", style="Valeur.TLabel")
            v.pack(anchor="w")
            d = ttk.Label(c, text="", style="CarteMuet.TLabel", wraplength=380, justify="left")
            d.pack(anchor="w")
            self.valeurs[cle] = (v, d)
        for j in range(3):
            cartes.columnconfigure(j, weight=1)

        bas = ttk.Frame(self)
        bas.pack(fill="both", expand=True, pady=(10, 0))
        acces = T.carte(bas, "Accès rapide aux visualisations")
        acces.pack(side="left", fill="both", expand=True, padx=6)
        for cle, txt in [("etudiants", "Gérer les étudiants"), ("s1", "S1 – recherche séquentielle animée"),
                         ("s2", "S2 – insertion avec décalages"), ("s3", "S3 – arbre binaire de recherche"),
                         ("visu", "Animations : tri rapide, insertion, dichotomie, tas, ABR"),
                         ("tas", "Bonus 1 – top-k par tas max"), ("equi", "Bonus 2 – ABR équilibré"),
                         ("exp", "Lancer l'étude expérimentale"), ("cmp", "Courbes de complexité")]:
            ttk.Button(acces, text="→  " + txt, command=lambda c=cle: app.aller(c)).pack(fill="x", pady=2)

        info = T.carte(bas, "Structures (même contenu, même ordre d'arrivée)")
        info.pack(side="left", fill="both", expand=True, padx=6)
        self.arbre = ttk.Treeview(info, columns=("taille", "mem", "rech"), show="tree headings", height=6)
        self.arbre.heading("#0", text="Structure")
        self.arbre.heading("taille", text="Taille")
        self.arbre.heading("mem", text="Mémoire")
        self.arbre.heading("rech", text="Recherche (µs, mesurée en C)")
        self.arbre.column("#0", width=200)
        for c in ("taille", "mem", "rech"):
            self.arbre.column(c, width=110, anchor="e")
        self.arbre.pack(fill="both", expand=True)
        ttk.Button(info, text="Mesurer maintenant (clock(), C)", command=self.mesurer).pack(anchor="e", pady=6)
        ttk.Label(info, text="Choix de la structure de référence :", style="CarteMuet.TLabel").pack(anchor="w")
        self.choix = tk.IntVar(value=app.structure_choisie)
        for s in range(4):
            ttk.Radiobutton(info, text=NOMS_STRUCTURES[s], variable=self.choix, value=s, style="Carte.TRadiobutton",
                            command=self._choisir).pack(anchor="w")

    def _choisir(self):
        self.app.structure_choisie = self.choix.get()
        self.rafraichir()

    def mesurer(self):
        self.rafraichir(mesure=True)

    def rafraichir(self, mesure=False):
        b = self.b
        n = b.taille()
        st = b.abr_stats()
        mem = sum(b.memoire(s) for s in range(4))
        self.valeurs["total"][0].config(text=str(n))
        self.valeurs["total"][1].config(text="taille courante de la base (4 structures synchronisées)")
        self.valeurs["structure"][0].config(text=NOMS_STRUCTURES[self.app.structure_choisie].split("–")[0])
        self.valeurs["structure"][1].config(text=NOMS_STRUCTURES[self.app.structure_choisie])
        self.valeurs["hauteur"][0].config(text=str(st["hauteur"]))
        self.valeurs["hauteur"][1].config(text=f"minimum possible {st['hmin']} ; sous-arbres racine {st['hg']} / {st['hd']}")
        self.valeurs["memoire"][0].config(text=f"{mem / 1024:.1f} Ko")
        self.valeurs["memoire"][1].config(text="somme des 4 structures")
        xs, ser = data.charger("recherche")
        if xs:
            s = {0: "S1_tableau_moyen", 1: "S1_liste_moyen", 2: "S2_moyen", 3: "S3_moyen"}[self.app.structure_choisie]
            self.valeurs["temps"][0].config(text=f"{ser[s][-1]:.3f} µs")
            self.valeurs["temps"][1].config(text=f"{s}, n = {xs[-1]} (résultats/recherche.csv)")
        proto = data.protocole()
        if proto:
            lignes = dict(l.split(":", 1) for l in proto.splitlines() if ":" in l)
            self.valeurs["exp"][0].config(text=lignes.get("Duree totale            ", " —").strip())
            self.valeurs["exp"][1].config(text=(lignes.get("Date                    ", "").strip() + " — tailles"
                                                + lignes.get("Tailles n               ", "")))
        else:
            self.valeurs["exp"][0].config(text="aucune")
            self.valeurs["exp"][1].config(text="lancer l'étude dans « Étude expérimentale »")
        self.arbre.delete(*self.arbre.get_children())
        cle = b.trie(2)[n // 2].cle if n else 0
        for s in range(4):
            t = f"{b.mesurer(0, s, cle)[0]:.3f}" if (mesure and n) else "—"
            self.arbre.insert("", "end", text=NOMS_STRUCTURES[s], values=(n, f"{b.memoire(s) / 1024:.1f} Ko", t))

    def base_modifiee(self):
        pass
