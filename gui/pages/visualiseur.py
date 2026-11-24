"""
Visualiseur d'algorithmes : chaque animation rejoue la trace émise par la VRAIE
fonction C (tri_rapide, tri_insertion / inserer_dans_trie, s2_rechercher,
construire_tas_max / entasser / extraire_max, inserer_abr / abr_supprimer ...).
"""
import random
import tkinter as tk
from tkinter import ttk, messagebox
import theme as T
import frames as F
from widgets import Lecteur, VueTableau, VueArbre, VueTas, legende
from backend import CAS_ABR, cle_depuis_moyenne

PSEUDO = {
    "rapide": """TRI RAPIDE (partition de Lomuto) — tris.c
tri_rapide(t, g, d):
  tant que g < d:
    p ← partition(t, g, d)
    trier récursivement la plus petite partie,
    boucler sur la plus grande (pile O(log n))
partition(t, g, d):
  [pivot médian de 3 amené en t[d]]
  i ← g-1
  pour j de g à d-1:
     si t[j] ≤ pivot: i++, échanger t[i], t[j]
  échanger t[i+1], t[d]   → pivot à sa place
Coût : Θ(n log n) moyen, Θ(n²) pire""",
    "insertion": """TRI PAR INSERTION — tris.c
pour i de 1 à n-1:
   x ← t[i]            (mis de côté)
   j ← i-1
   tant que j ≥ 0 et t[j] > x:
       t[j+1] ← t[j]   (décalage)
       j ← j-1
   t[j+1] ← x
inserer_dans_trie() est la fonction
utilisée par S2 à chaque ajout.
Coût : Θ(n) meilleur, Θ(n²) pire""",
    "dicho": """RECHERCHE DICHOTOMIQUE — s2_trie.c
g ← 0 ; d ← n-1
tant que g ≤ d:
   m ← g + (d-g)/2
   si t[m] = x : trouvé
   si t[m] < x : g ← m+1
   sinon       : d ← m-1
Comptage : deux dichotomies
(borne inf. et borne sup.)
Coût : Θ(log n)""",
    "tas": """TAS MAX — tas.c (TP3)
Entasser(t, taille, i):
  max ← i parmi i, 2i+1, 2i+2
  si max ≠ i: échanger, Entasser(max)
ConstruireTasMax(t, n):
  pour i de n/2-1 à 0: Entasser(i)
Top-k : k fois
  échanger t[0] et t[taille-1]
  taille-- ; Entasser(0)
Coût : Θ(n) + Θ(k log n)""",
    "abr": """ABR — s3_abr.c
Insertion : descente, gauche si plus petit
 (clé = (moyenne, matricule)).
Suppression :
  1. feuille   → retirée
  2. un fils   → le père adopte le fils
  3. deux fils → copie du successeur
     (min du sous-arbre droit), puis
     retrait du successeur
Construction équilibrée (bonus 2) :
  insérer le milieu, puis chaque moitié.""",
}


def valeurs_demo(n, ordre):
    v = [random.randint(200, 1950) for _ in range(n)]
    if ordre == "croissant":
        v.sort()
    elif ordre == "décroissant":
        v.sort(reverse=True)
    return v


class Onglet(ttk.Frame):
    def __init__(self, parent, app, cle, vue, legende_items):
        super().__init__(parent, padding=8)
        self.app, self.b = app, app.b
        self.barre = ttk.Frame(self, style="Carte.TFrame", padding=8)
        self.barre.pack(fill="x")
        corps = ttk.Frame(self)
        corps.pack(fill="both", expand=True, pady=6)
        cv = ttk.Frame(corps, style="Carte.TFrame", padding=6)
        cv.pack(side="left", fill="both", expand=True)
        self.vue = vue(cv)
        self.vue.pack(fill="both", expand=True)
        legende(cv, legende_items).pack(anchor="w", pady=(4, 0))
        droite = T.carte(corps, "Algorithme")
        droite.pack(side="left", fill="y", padx=(8, 0))
        t = T.texte(droite, hauteur=18, width=44)
        t.insert("1.0", PSEUDO[cle])
        t.config(state="disabled")
        t.pack(fill="y")
        self.infos = ttk.Label(droite, text="", style="Carte.TLabel", justify="left", font=T.MONO)
        self.infos.pack(anchor="w", pady=6)
        self.message = ttk.Label(self, text="", style="Sous.TLabel", wraplength=1050)
        self.message.pack(anchor="w")
        self.lecteur = Lecteur(self, self._rendu, lambda m: self.message.config(text=m))
        self.lecteur.pack(fill="x")

    def _rendu(self, img):
        self.vue.dessiner(img)
        st = img.get("stats")
        if st:
            self.infos.config(text=f"Comparaisons : {st['cmp']}\nÉchanges     : {st['ech']}\nDécalages    : {st['dec']}")

    def champ_valeurs(self, defaut_n=16):
        ttk.Label(self.barre, text="n", style="Carte.TLabel").pack(side="left")
        self.n = ttk.Spinbox(self.barre, from_=2, to=60, width=4)
        self.n.set(defaut_n)
        self.n.pack(side="left", padx=4)
        self.ordre = ttk.Combobox(self.barre, values=["aléatoire", "croissant", "décroissant"], state="readonly", width=11)
        self.ordre.current(0)
        self.ordre.pack(side="left", padx=4)
        ttk.Label(self.barre, text="ou valeurs :", style="Carte.TLabel").pack(side="left", padx=(8, 2))
        self.saisie = ttk.Entry(self.barre, width=30)
        self.saisie.pack(side="left")

    def valeurs(self):
        txt = self.saisie.get().strip()
        if txt:
            try:
                v = [cle_depuis_moyenne(float(x.replace(",", "."))) for x in txt.replace(";", " ").split()]
                if all(0 <= x <= 2000 for x in v) and len(v) >= 1:
                    return v[:60]
            except ValueError:
                pass
            messagebox.showwarning("Valeurs", "Saisir des moyennes entre 0 et 20 séparées par des espaces.")
            return None
        try:
            n = max(2, min(60, int(self.n.get())))
        except ValueError:
            n = 16
        return valeurs_demo(n, self.ordre.get())


ARRAY_LEG = [(T.C_COMPARE, "comparaison"), (T.C_SWAP, "échange"), (T.C_SHIFT, "décalage"),
             (T.C_PIVOT, "pivot / élément mis de côté"), (T.C_TRIE, "à sa place"), (T.C_INTERVALLE, "partition")]


class OngletRapide(Onglet):
    def __init__(self, p, app):
        super().__init__(p, app, "rapide", lambda c: VueTableau(c, hauteur=380), ARRAY_LEG)
        self.champ_valeurs()
        self.pivot = ttk.Combobox(self.barre, values=["pivot médian de 3", "pivot dernier"], state="readonly", width=16)
        self.pivot.current(0)
        self.pivot.pack(side="left", padx=6)
        ttk.Button(self.barre, text="Exécuter en C", style="Accent.TButton", command=self.lancer).pack(side="left", padx=4)

    def lancer(self):
        v = self.valeurs()
        if v is None:
            return
        evs, res = self.b.anim_tri_rapide(v, self.pivot.current() == 1)
        self.lecteur.charger(F.frames_tableau(v, evs, final=res))


class OngletInsertion(Onglet):
    def __init__(self, p, app):
        super().__init__(p, app, "insertion", lambda c: VueTableau(c, hauteur=380), ARRAY_LEG)
        self.champ_valeurs(14)
        ttk.Button(self.barre, text="Exécuter en C", style="Accent.TButton", command=self.lancer).pack(side="left", padx=4)

    def lancer(self):
        v = self.valeurs()
        if v is None:
            return
        evs, res = self.b.anim_tri_insertion(v)
        self.lecteur.charger(F.frames_tableau(v, evs, final=res))


class OngletDicho(Onglet):
    def __init__(self, p, app):
        super().__init__(p, app, "dicho", lambda c: VueTableau(c, hauteur=380),
                         [(T.C_COMPARE, "milieu m"), (T.C_HORS, "hors intervalle [g, d]"), (T.C_TROUVE, "trouvé")])
        self.champ_valeurs(24)
        ttk.Label(self.barre, text="cherchée", style="Carte.TLabel").pack(side="left", padx=(8, 2))
        self.cible = ttk.Entry(self.barre, width=7)
        self.cible.pack(side="left")
        self.mode = ttk.Combobox(self.barre, values=["existence", "comptage (2 bornes)"], state="readonly", width=17)
        self.mode.current(0)
        self.mode.pack(side="left", padx=4)
        ttk.Button(self.barre, text="Exécuter en C", style="Accent.TButton", command=self.lancer).pack(side="left", padx=4)

    def lancer(self):
        v = self.valeurs()
        if v is None:
            return
        try:
            cle = cle_depuis_moyenne(float(self.cible.get().replace(",", ".")))
        except ValueError:
            cle = random.choice(v)
            self.cible.delete(0, "end")
            self.cible.insert(0, f"{cle / 100:.2f}")
        evs, trie, r = self.b.anim_dichotomie(v, cle, self.mode.current() == 1)
        imgs = F.frames_tableau(trie, evs, cle_cherchee=cle, titre=f"Tableau trié (construit par s2_ajouter) — on cherche {cle / 100:.2f}")
        imgs[-1]["msg"] += f"   → résultat C : {r}"
        self.lecteur.charger(imgs)


class OngletTas(Onglet):
    def __init__(self, p, app):
        super().__init__(p, app, "tas", VueTas, [(T.C_PIVOT, "Entasser(i)"), (T.C_COMPARE, "comparaison"),
                                                 (T.C_SWAP, "échange"), (T.C_TRIE, "hors du tas (extrait)"),
                                                 (T.C_TROUVE, "maximum")])
        self.champ_valeurs(15)
        ttk.Label(self.barre, text="k", style="Carte.TLabel").pack(side="left", padx=(8, 2))
        self.k = ttk.Spinbox(self.barre, from_=0, to=60, width=4)
        self.k.set(4)
        self.k.pack(side="left")
        ttk.Button(self.barre, text="Exécuter en C", style="Accent.TButton", command=self.lancer).pack(side="left", padx=4)

    def lancer(self):
        v = self.valeurs()
        if v is None:
            return
        try:
            k = max(0, min(len(v), int(self.k.get())))
        except ValueError:
            k = 3
        evs, ext = self.b.anim_tas(v, k)
        imgs = F.frames_tableau(v, evs, titre="Copie du tableau avant ConstruireTasMax")
        if imgs:
            imgs[-1]["msg"] = f"Top-{k} par tas max : " + ", ".join(f"{x / 100:.2f}" for x in ext)
        self.lecteur.charger(imgs)


class OngletABR(Onglet):
    def __init__(self, p, app):
        super().__init__(p, app, "abr", lambda c: VueArbre(c, hauteur=400),
                         [(T.C_SWAP, "nœud courant"), (T.C_COMPARE, "chemin"), (T.C_TROUVE, "trouvé"),
                          (T.C_SUCC, "successeur"), (T.C_TRIE, "inséré")])
        self.champ_valeurs(12)
        self.equi = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.barre, text="équilibré", variable=self.equi).pack(side="left", padx=4)
        ttk.Button(self.barre, text="Construire", style="Accent.TButton", command=self.construire).pack(side="left", padx=4)
        b2 = ttk.Frame(self, style="Carte.TFrame", padding=(8, 0, 8, 8))
        b2.pack(fill="x", after=self.barre)
        ttk.Label(b2, text="Moyenne", style="Carte.TLabel").pack(side="left")
        self.cle = ttk.Entry(b2, width=7)
        self.cle.pack(side="left", padx=4)
        for txt, fn in [("Insérer", self.inserer), ("Rechercher", self.rechercher), ("Compter", self.compter),
                        ("Supprimer", self.supprimer), ("Top-3", self.topk), ("Arbre démo 3 cas", self.demo_cas),
                        ("Cas feuille", lambda: self.supprimer(700)), ("Cas un fils", lambda: self.supprimer(300)),
                        ("Cas deux fils", lambda: self.supprimer(1000))]:
            ttk.Button(b2, text=txt, command=fn).pack(side="left", padx=2)
        self.etat_label = ttk.Label(b2, text="", style="CarteMuet.TLabel")
        self.etat_label.pack(side="left", padx=10)

    def _cle(self):
        try:
            return cle_depuis_moyenne(float(self.cle.get().replace(",", ".")))
        except ValueError:
            messagebox.showwarning("Moyenne", "Saisir une moyenne.")
            return None

    def _charger(self, avant, evs, apres, cle=None, msg_fin=None):
        imgs = F.frames_arbre(avant, evs, apres, cles_cherchee=cle)
        if msg_fin:
            imgs[-1]["msg"] = msg_fin
        self.lecteur.charger(imgs)
        self.etat_label.config(text=f"hauteur de l'ABR (C) : {self.b.anim_abr_hauteur()}")

    def construire(self):
        v = self.valeurs()
        if v is None:
            return
        evs = self.b.anim_abr_sequence(v, self.equi.get())
        apres = self.b.anim_abr_exporter()
        self._charger(None, evs, apres, msg_fin=f"Construction terminée : hauteur {self.b.anim_abr_hauteur()}")

    def inserer(self):
        cle = self._cle()
        if cle is None:
            return
        avant = self.b.anim_abr_exporter()
        evs = self.b.anim_abr_inserer(cle)
        self._charger(avant, evs, self.b.anim_abr_exporter(), cle)

    def rechercher(self):
        cle = self._cle()
        if cle is None:
            return
        avant = self.b.anim_abr_exporter()
        evs, r = self.b.anim_abr_rechercher(cle)
        self._charger(avant, evs, None, cle, f"Résultat : {'trouvée' if r >= 0 else 'absente'}")

    def compter(self):
        cle = self._cle()
        if cle is None:
            return
        avant = self.b.anim_abr_exporter()
        evs, r = self.b.anim_abr_compter(cle)
        self._charger(avant, evs, None, cle, f"{r} nœud(s) de moyenne {cle / 100:.2f} (parcours élagué)")

    def supprimer(self, cle=None):
        cle = cle if cle is not None else self._cle()
        if cle is None:
            return
        avant = self.b.anim_abr_exporter()
        evs, ok, cas = self.b.anim_abr_supprimer(cle)
        self._charger(avant, evs, self.b.anim_abr_exporter(), cle,
                      f"Suppression : {CAS_ABR.get(cas, 'absente') if ok else 'moyenne absente'}")

    def topk(self):
        avant = self.b.anim_abr_exporter()
        evs, res = self.b.anim_abr_topk(3)
        self._charger(avant, evs, None, None, "Top-3 (infixe inverse) : " + ", ".join(f"{x / 100:.2f}" for x in res))

    def demo_cas(self):
        """Arbre fixe : 7.00 est une feuille, 3.00 a un seul fils, 10.00 (racine) a deux fils."""
        v = [1000, 500, 1500, 300, 700, 1200, 1800, 400, 1100, 1300]
        evs = self.b.anim_abr_sequence(v, False)
        self._charger(None, evs, self.b.anim_abr_exporter(),
                      msg_fin="Arbre de démonstration : utilisez « Cas feuille » (7.00), « Cas un fils » (3.00), "
                              "« Cas deux fils » (10.00)")


class PageVisualiseur(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        ttk.Label(self, text="Visualiseur d'algorithmes", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="Les animations rejouent pas à pas la trace d'exécution des fonctions C du projet "
                             "(aucun algorithme n'est réécrit en Python).", style="Muet.TLabel").pack(anchor="w", pady=(0, 6))
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True)
        for nom, classe in [("Tri rapide", OngletRapide), ("Tri par insertion", OngletInsertion),
                            ("Recherche dichotomique", OngletDicho), ("Tas max", OngletTas), ("ABR", OngletABR)]:
            nb.add(classe(nb, app), text=nom)
