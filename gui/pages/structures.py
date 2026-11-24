"""
Pages S1, S2, S3 : opérations sur la VRAIE base (bibliothèque C) avec animation
de la trace d'exécution lorsque la base est assez petite pour être dessinée.
"""
import random
import tkinter as tk
from tkinter import ttk, messagebox
import theme as T
import frames as F
from widgets import Lecteur, VueTableau, VueListe, VueArbre, legende
from backend import S1_TABLEAU, S1_LISTE, S2_TRIE, S3_ABR, NOMS_STRUCTURES, CAS_ABR, cle_depuis_moyenne

LIMITE_ANIM = 64

DESCRIPTIONS = {
    "S1": ("S1 – Liste non triée",
           "Étudiants rangés dans l'ordre d'arrivée. Implémentation retenue : tableau dynamique (ajout en fin "
           "Θ(1) amorti, accès direct pour le tri rapide, parcours favorable au cache). La variante liste "
           "chaînée sert à mesurer l'effet du choix.",
           ["Ajout : Θ(1) amorti (fin du tableau / queue de liste)",
            "Recherche : Θ(1) meilleur, Θ(n) moyen et pire (séquentielle)",
            "Comptage : Θ(n) (parcours complet)",
            "Suppression : tableau Θ(n) (recherche + décalages) ; liste Θ(1)..Θ(n)",
            "Affichage trié : copie + tri rapide Θ(n log n), Θ(n²) au pire",
            "Top-k : tri rapide puis k derniers Θ(n log n)",
            "Mémoire : capacité × 104 o (tableau) ; n × 112 o (liste)"]),
    "S2": ("S2 – Tableau trié",
           "Ordre croissant maintenu à chaque ajout (principe du tri par insertion : décalage des plus grands). "
           "Recherche par dichotomie ; top-k par lecture directe des k derniers.",
           ["Ajout : Θ(1) meilleur (plus grande moyenne), Θ(n) moyen et pire",
            "Recherche : Θ(1) meilleur (milieu), Θ(log n) moyen et pire",
            "Comptage : Θ(log n) (bornes inférieure et supérieure)",
            "Suppression : Θ(log n) + décalages : Θ(log n) .. Θ(n)",
            "Affichage trié : Θ(n) (déjà trié)",
            "Top-k : Θ(k) (accès direct)"]),
    "S3": ("S3 – Arbre binaire de recherche",
           "ABR indexé sur la moyenne ; les moyennes égales sont départagées par le matricule (clé composée), "
           "donc un étudiant arrivé plus tard va à droite. Suppression : feuille, un fils, deux fils "
           "(successeur = minimum du sous-arbre droit).",
           ["Ajout : Θ(h) : Θ(log n) aléatoire, Θ(n) dégénéré",
            "Recherche : Θ(1) racine, Θ(log n) moyen, Θ(n) dégénéré",
            "Comptage : Θ(h + d) (parcours élagué des doublons)",
            "Suppression : Θ(h) dans les trois cas",
            "Affichage trié : parcours infixe Θ(n)",
            "Top-k : infixe inverse arrêté après k : Θ(h + k)"]),
}


class PageStructure(ttk.Frame):
    code = "S1"

    def __init__(self, parent, app):
        super().__init__(parent)
        self.app, self.b = app, app.b
        titre, desc, cplx = DESCRIPTIONS[self.code]
        ttk.Label(self, text=titre, style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text=desc, style="Muet.TLabel", wraplength=1100, justify="left").pack(anchor="w", pady=(0, 8))
        corps = ttk.Frame(self)
        corps.pack(fill="both", expand=True)
        gauche = ttk.Frame(corps, width=430)
        gauche.pack(side="left", fill="y")
        gauche.pack_propagate(False)
        droite = ttk.Frame(corps)
        droite.pack(side="left", fill="both", expand=True, padx=(12, 0))

        op = T.carte(gauche, "Opérations")
        op.pack(fill="x")
        self._options_struct(op)
        ligne = ttk.Frame(op, style="Carte.TFrame")
        ligne.pack(fill="x", pady=2)
        ttk.Label(ligne, text="Moyenne", style="Carte.TLabel").pack(side="left")
        self.moy = ttk.Entry(ligne, width=7)
        self.moy.insert(0, "12.50")
        self.moy.pack(side="left", padx=4)
        ttk.Label(ligne, text="k", style="Carte.TLabel").pack(side="left")
        self.k = ttk.Spinbox(ligne, from_=1, to=10000, width=5)
        self.k.set(5)
        self.k.pack(side="left", padx=4)
        g = ttk.Frame(op, style="Carte.TFrame")
        g.pack(fill="x")
        for i, (txt, fn) in enumerate([("Ajouter (moyenne)", self.op_ajouter), ("Ajouter (aléatoire)", self.op_ajouter_alea),
                                       ("Rechercher", self.op_rechercher), ("Compter", self.op_compter),
                                       ("Supprimer", self.op_supprimer), ("Affichage trié", self.op_trie),
                                       ("Top-k", self.op_topk), ("Base démo (n = 15)", self.op_demo)]):
            ttk.Button(g, text=txt, command=fn).grid(row=i // 2, column=i % 2, sticky="we", padx=2, pady=2)
        g.columnconfigure(0, weight=1)
        g.columnconfigure(1, weight=1)

        c = T.carte(gauche, "Complexités théoriques")
        c.pack(fill="x", pady=8)
        for l in cplx:
            ttk.Label(c, text="• " + l, style="CarteMuet.TLabel", wraplength=390, justify="left").pack(anchor="w")

        s = T.carte(gauche, "État et coût de la dernière opération")
        s.pack(fill="both", expand=True)
        self.stats = ttk.Label(s, text="", style="Carte.TLabel", justify="left", font=T.MONO)
        self.stats.pack(anchor="w")

        vis = T.carte(droite)
        vis.pack(fill="both", expand=True)
        self.vue = self._creer_vue(vis)
        self.vue.pack(fill="both", expand=True)
        legende(vis, self._legende()).pack(anchor="w", pady=(4, 0))
        self.message = ttk.Label(droite, text="", style="Sous.TLabel", wraplength=1000)
        self.message.pack(anchor="w", pady=(6, 2))
        self.lecteur = Lecteur(droite, self.vue.dessiner, lambda t: self.message.config(text=t))
        self.lecteur.pack(fill="x")
        self.journal = T.texte(droite, hauteur=7)
        self.journal.pack(fill="x", pady=(6, 0))
        self.dernier = {}

    # ---- à spécialiser ----
    def _options_struct(self, parent):
        pass

    def structure(self):
        return {"S1": S1_TABLEAU, "S2": S2_TRIE, "S3": S3_ABR}[self.code]

    def _creer_vue(self, parent):
        return VueTableau(parent, hauteur=340, mode="cases")

    def _legende(self):
        return [(T.C_COMPARE, "comparaison"), (T.C_SHIFT, "décalage"), (T.C_SWAP, "échange"),
                (T.C_PIVOT, "pivot / élément inséré"), (T.C_TRIE, "placé / trié"), (T.C_TROUVE, "trouvé")]

    # ---- utilitaires ----
    def rafraichir(self):
        self.afficher_etat()
        self.maj_stats()

    def base_modifiee(self):
        if self.winfo_ismapped():
            self.rafraichir()

    def cles(self):
        return [e.cle for e in self.b.contenu(self.structure())]

    def afficher_etat(self, msg=None):
        arr = self.cles()
        if len(arr) > LIMITE_ANIM:
            arr = arr[:LIMITE_ANIM]
        img = dict(arr=arr, roles={}, msg=msg or "")
        self.lecteur.charger([img], jouer=False)
        if msg is None:
            n = self.b.taille()
            self.message.config(text=f"{n} étudiants" + (f" — seuls les {LIMITE_ANIM} premiers sont dessinés ; "
                                                         f"animations disponibles pour n ≤ {LIMITE_ANIM} "
                                                         f"(bouton « Base démo »)" if n > LIMITE_ANIM else ""))

    def maj_stats(self, extra=""):
        s = self.structure()
        n = self.b.taille()
        txt = f"Taille      : {n}\nMémoire     : {self.b.memoire(s) / 1024:.1f} Ko\n"
        if self.dernier:
            d = self.dernier
            txt += (f"\nOpération   : {d.get('op', '')}\nComparaisons: {d['comparaisons']}\n"
                    f"Mouvements  : {d['mouvements']}\nVisites     : {d['visites']}\n")
            if d.get("temps") is not None:
                txt += f"Temps (C)   : {d['temps']:.3f} µs\n"
        self.stats.config(text=txt + extra)

    def lire_cle(self):
        try:
            m = float(self.moy.get().replace(",", "."))
            if not 0 <= m <= 20:
                raise ValueError
            return cle_depuis_moyenne(m)
        except ValueError:
            messagebox.showwarning("Moyenne", "Saisir une moyenne entre 0 et 20.")
            return None

    def lire_k(self):
        try:
            return max(1, int(self.k.get()))
        except ValueError:
            return 5

    def log(self, texte, tag=None):
        self.journal.insert("end", texte + "\n", tag)
        self.journal.see("end")

    def apres_operation(self, nom, initial, final=None, cle=None, temps=None, mesure=None, titre="État initial"):
        evs = self.b.trace()
        self.dernier = dict(self.b.compteurs(), op=nom, temps=temps)
        if mesure is not None:
            self.dernier["temps"] = mesure
        self.app.maj_statut(f"{nom} ({NOMS_STRUCTURES[self.structure()]})")
        if self.b.taille() <= LIMITE_ANIM + 1 and len(initial) <= LIMITE_ANIM + 1:
            imgs = F.frames_tableau(initial, evs, final=final, cle_cherchee=cle, titre=titre)
            self.lecteur.charger(imgs)
        else:
            self.afficher_etat(f"{nom} : base trop grande pour l'animation ({len(evs)} événements tracés) — "
                               f"coût affiché à gauche")
        self.maj_stats()

    # ---- opérations ----
    def _ajouter(self, cle):
        s = self.structure()
        avant = self.cles()
        note = cle / 100.0
        ident, err = self.b.ajouter("Demo", random.choice(["Amine", "Lina", "Idir", "Sarah"]), 20,
                                    random.choice("MF"), [note] * 5, trace_structure=s)
        if err:
            self.log("Erreur : " + err, "err")
            return
        self.log(f"Ajout du matricule {ident}, moyenne {note:.2f}", "ok")
        self.app.base_modifiee()
        self.apres_ajout(avant, cle)

    def apres_ajout(self, avant, cle):
        self.apres_operation("ajout", avant, final=self.cles(), cle=cle)

    def op_ajouter(self):
        cle = self.lire_cle()
        if cle is not None:
            self._ajouter(cle)

    def op_ajouter_alea(self):
        self._ajouter(random.randint(400, 1900))

    def op_rechercher(self):
        cle = self.lire_cle()
        if cle is None:
            return
        s = self.structure()
        avant = self.cles()
        ok = self.b.rechercher(s, cle, trace=True)
        evs_c = self.b.compteurs()
        t, _ = self.b.mesurer(0, s, cle)
        self.b.rechercher(s, cle, trace=True)     # retrace (la mesure vide la trace)
        self.log(f"Recherche de {cle / 100:.2f} : {'trouvée' if ok else 'absente'} — "
                 f"{evs_c['comparaisons']} comparaisons, {t:.3f} µs", "ok" if ok else "err")
        self.apres_recherche(avant, cle, t)

    def apres_recherche(self, avant, cle, t):
        self.apres_operation("recherche", avant, cle=cle, mesure=t)

    def op_compter(self):
        cle = self.lire_cle()
        if cle is None:
            return
        s = self.structure()
        avant = self.cles()
        t, _ = self.b.mesurer(1, s, cle)
        nb = self.b.compter(s, cle, trace=True)
        self.log(f"Nombre d'étudiants de moyenne {cle / 100:.2f} : {nb} — {t:.3f} µs")
        self.apres_recherche(avant, cle, t)

    def op_supprimer(self):
        cle = self.lire_cle()
        if cle is None:
            return
        avant = self.cles()
        avant_export = self.b.abr_exporter() if self.code == "S3" else None
        e, cas = self.b.supprimer(cle, -1, trace_structure=self.structure())
        if not e:
            self.log(f"Aucun étudiant de moyenne {cle / 100:.2f}", "err")
            self.dernier = {}
            return
        self.log(f"Suppression du matricule {e.id} ({e.moyenne:.2f})" +
                 (f" — cas ABR : {CAS_ABR.get(cas)}" if self.code == "S3" else ""), "ok")
        self.app.base_modifiee()
        self.apres_suppression(avant, avant_export, cle)

    def apres_suppression(self, avant, avant_export, cle):
        self.apres_operation("suppression", avant, final=self.cles(), cle=cle)

    def op_trie(self):
        s = self.structure()
        avant = self.cles()
        t, _ = self.b.mesurer(2, s)
        liste = self.b.trie(s, trace=True)
        self.log(f"Affichage trié : {len(liste)} étudiants — {t:.3f} µs ; premiers : " +
                 ", ".join(f"{e.moyenne:.2f}" for e in liste[:12]))
        self.apres_trie(avant, t, liste)

    def apres_trie(self, avant, t, liste):
        self.apres_operation("affichage trié", avant, mesure=t, titre="Copie de S1 avant le tri rapide")

    def op_topk(self):
        s, k = self.structure(), self.lire_k()
        avant = self.cles()
        t, _ = self.b.mesurer(3, s, k)
        liste = self.b.topk(s, k, trace=True)
        self.log(f"Top-{k} : " + ", ".join(f"{e.prenom} {e.nom} ({e.moyenne:.2f})" for e in liste[:10]) +
                 f" — {t:.3f} µs", "ok")
        self.apres_topk(avant, t, liste)

    def apres_topk(self, avant, t, liste):
        self.apres_operation("top-k", avant, mesure=t)

    def op_demo(self):
        self.b.generer(15, 0, random.randint(1, 10 ** 6))
        self.dernier = {}
        self.log("Base de démonstration : 15 étudiants aléatoires (dans les 4 structures)")
        self.app.base_modifiee()
        self.rafraichir()


# ====================================================================== #
class PageS1(PageStructure):
    code = "S1"

    def _options_struct(self, parent):
        ligne = ttk.Frame(parent, style="Carte.TFrame")
        ligne.pack(fill="x", pady=(0, 4))
        self.variante = tk.IntVar(value=S1_TABLEAU)
        ttk.Radiobutton(ligne, text="Tableau", variable=self.variante, value=S1_TABLEAU, style="Carte.TRadiobutton",
                        command=self._changer).pack(side="left")
        ttk.Radiobutton(ligne, text="Liste chaînée", variable=self.variante, value=S1_LISTE, style="Carte.TRadiobutton",
                        command=self._changer).pack(side="left", padx=6)
        l2 = ttk.Frame(parent, style="Carte.TFrame")
        l2.pack(fill="x", pady=(0, 4))
        ttk.Label(l2, text="Pivot du tri rapide", style="Carte.TLabel").pack(side="left")
        self.pivot = ttk.Combobox(l2, values=["médiane de 3", "dernier élément"], state="readonly", width=15)
        self.pivot.current(0)
        self.pivot.pack(side="left", padx=4)
        self.pivot.bind("<<ComboboxSelected>>", lambda e: self.b.definir_pivot(self.pivot.current() == 1))

    def structure(self):
        return self.variante.get()

    def _creer_vue(self, parent):
        self._cadre_vue = ttk.Frame(parent, style="Carte.TFrame")
        self._v_tab = VueTableau(self._cadre_vue, hauteur=340, mode="cases")
        self._v_liste = VueListe(self._cadre_vue, hauteur=340)
        self._v_tab.pack(fill="both", expand=True)
        self._cadre_vue.dessiner = lambda img: self._vue_active().dessiner(img)
        return self._cadre_vue

    def _vue_active(self):
        return self._v_liste if self.variante.get() == S1_LISTE else self._v_tab

    def _changer(self):
        (self._v_tab if self.variante.get() == S1_LISTE else self._v_liste).pack_forget()
        self._vue_active().pack(fill="both", expand=True)
        self.dernier = {}
        self.rafraichir()

    def apres_trie(self, avant, t, liste):
        self.apres_operation("affichage trié (copie + tri rapide)", avant, mesure=t,
                             titre="Copie de S1 (ordre d'arrivée) avant le tri rapide")

    def apres_topk(self, avant, t, liste):
        self.apres_operation("top-k (tri rapide puis k derniers)", avant, mesure=t,
                             titre="Copie de S1 avant le tri rapide")
        if self.lecteur.images:
            self.lecteur.images[-1]["msg"] = "k meilleurs = les k derniers du tableau trié : " + \
                ", ".join(f"{e.moyenne:.2f}" for e in liste)


class PageS2(PageStructure):
    code = "S2"


class PageS3(PageStructure):
    code = "S3"

    def _creer_vue(self, parent):
        return VueArbre(parent, hauteur=360)

    def _legende(self):
        return [(T.C_SWAP, "nœud courant"), (T.C_COMPARE, "chemin parcouru"), (T.C_TROUVE, "trouvé / retenu"),
                (T.C_SUCC, "successeur"), (T.C_TRIE, "nœud inséré")]

    def afficher_etat(self, msg=None):
        exp = self.b.abr_exporter()
        mod, rac = F.modele_depuis_export(exp)
        self.lecteur.charger([dict(mod=mod, rac=rac, roles={}, msg=msg or "")], jouer=False)
        if msg is None:
            self.message.config(text=f"{self.b.taille()} étudiants")

    def maj_stats(self, extra=""):
        st = self.b.abr_stats()
        desequilibre = st["hg"] - st["hd"]
        super().maj_stats(f"\nHauteur     : {st['hauteur']} (min {st['hmin']})\n"
                          f"Ss-arbres   : {st['hg']} / {st['hd']} (Δ = {desequilibre:+d})\n"
                          f"Feuilles    : {st['feuilles']}\nProf. moy.  : {st['prof']:.2f}\n")

    def _anim_arbre(self, nom, avant, apres, cle=None, mesure=None):
        evs = self.b.trace()
        self.dernier = dict(self.b.compteurs(), op=nom, temps=mesure)
        self.app.maj_statut(f"{nom} (S3)")
        imgs = F.frames_arbre(avant, evs, apres, cles_cherchee=cle)
        self.lecteur.charger(imgs)
        self.maj_stats()

    def apres_ajout(self, avant, cle):
        # trace déjà produite par l'ajout ; l'arbre « avant » = après sans le nœud inséré
        apres = self.b.abr_exporter()
        evs = self.b.trace()
        ins = [e for e in evs if e.type == 13]
        avant_exp = _sans_noeud(apres, ins[0].a) if ins else apres
        self.dernier = dict(self.b.compteurs(), op="ajout", temps=None)
        self.lecteur.charger(F.frames_arbre(avant_exp, evs, apres, cles_cherchee=cle))
        self.maj_stats()

    def apres_recherche(self, avant, cle, t):
        exp = self.b.abr_exporter()
        self._anim_arbre("recherche / comptage", exp, None, cle=cle, mesure=t)

    def apres_suppression(self, avant, avant_export, cle):
        self._anim_arbre("suppression", avant_export, self.b.abr_exporter(), cle=cle)

    def apres_trie(self, avant, t, liste):
        self._anim_arbre("parcours infixe", self.b.abr_exporter(), None, mesure=t)

    def apres_topk(self, avant, t, liste):
        self._anim_arbre("top-k (infixe inverse)", self.b.abr_exporter(), None, mesure=t)


def _sans_noeud(exp, ident):
    """Export de l'arbre sans la feuille `ident` (état avant son insertion)."""
    from backend import ArbreExport
    if ident not in exp.ids:
        return exp
    k = exp.ids.index(ident)
    ids, cles, fg, fd = [], [], [], []
    ancien_vers_nouveau = {}
    for i in range(len(exp.ids)):
        if i == k:
            continue
        ancien_vers_nouveau[i] = len(ids)
        ids.append(exp.ids[i]); cles.append(exp.cles[i]); fg.append(exp.fg[i]); fd.append(exp.fd[i])
    conv = lambda j: -1 if j < 0 or j == k else ancien_vers_nouveau[j]
    return ArbreExport(ids, cles, [conv(j) for j in fg], [conv(j) for j in fd])
