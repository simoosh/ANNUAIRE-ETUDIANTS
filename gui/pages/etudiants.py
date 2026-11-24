"""Gestion des étudiants : ajout validé, génération, recherche, suppression, top-k, détails."""
import tkinter as tk
from tkinter import ttk, messagebox
import theme as T
from backend import MATIERES, NOMS_STRUCTURES, cle_depuis_moyenne

COLONNES = ("id", "nom", "prenom", "age", "sexe", "n1", "n2", "n3", "n4", "n5", "moy")


class PageEtudiants(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app, self.b = app, app.b
        ttk.Label(self, text="Gestion des étudiants", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="Chaque opération est exécutée par la bibliothèque C sur les 4 structures "
                             "(S1 tableau, S1 liste, S2, S3), qui restent synchronisées.",
                  style="Muet.TLabel").pack(anchor="w", pady=(0, 10))
        corps = ttk.Frame(self)
        corps.pack(fill="both", expand=True)
        gauche = ttk.Frame(corps, width=360)
        gauche.pack(side="left", fill="y")
        droite = ttk.Frame(corps)
        droite.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # ---- formulaire d'ajout ----
        f = T.carte(gauche, "Ajouter un étudiant", grille=True)
        f.pack(fill="x", pady=(0, 8))
        self.champs = {}
        for i, (cle, lab) in enumerate([("nom", "Nom"), ("prenom", "Prénom"), ("age", "Âge")]):
            ttk.Label(f, text=lab, style="Carte.TLabel").grid(row=i + 1, column=0, sticky="w", pady=2)
            e = ttk.Entry(f, width=22)
            e.grid(row=i + 1, column=1, columnspan=3, sticky="we", pady=2)
            self.champs[cle] = e
        ttk.Label(f, text="Sexe", style="Carte.TLabel").grid(row=4, column=0, sticky="w")
        self.sexe = tk.StringVar(value="M")
        ttk.Radiobutton(f, text="M", variable=self.sexe, value="M", style="Carte.TRadiobutton").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(f, text="F", variable=self.sexe, value="F", style="Carte.TRadiobutton").grid(row=4, column=2, sticky="w")
        self.notes = []
        for j, mat in enumerate(MATIERES):
            ttk.Label(f, text=mat, style="Carte.TLabel").grid(row=5 + j, column=0, sticky="w", pady=1)
            e = ttk.Entry(f, width=8)
            e.grid(row=5 + j, column=1, sticky="w", pady=1)
            self.notes.append(e)
        ttk.Button(f, text="Ajouter", style="Accent.TButton", command=self.ajouter).grid(row=11, column=0, columnspan=4, sticky="we", pady=(8, 0))
        self.msg = ttk.Label(f, text="", style="CarteMuet.TLabel", wraplength=300)
        self.msg.grid(row=12, column=0, columnspan=4, sticky="w")

        # ---- génération ----
        g = T.carte(gauche, "Générer une base aléatoire (rand())", grille=True)
        g.pack(fill="x", pady=(0, 8))
        ttk.Label(g, text="n =", style="Carte.TLabel").grid(row=1, column=0)
        self.n = ttk.Spinbox(g, from_=1, to=200000, width=8)
        self.n.set(1000)
        self.n.grid(row=1, column=1, padx=4)
        self.mode = ttk.Combobox(g, values=["aléatoire", "croissant", "décroissant"], state="readonly", width=11)
        self.mode.current(0)
        self.mode.grid(row=1, column=2, padx=4)
        ttk.Label(g, text="graine", style="Carte.TLabel").grid(row=2, column=0)
        self.graine = ttk.Spinbox(g, from_=0, to=10 ** 6, width=8)
        self.graine.set(2026)
        self.graine.grid(row=2, column=1, padx=4, pady=4)
        ttk.Button(g, text="Générer", command=self.generer).grid(row=2, column=2, sticky="we")

        # ---- recherche / suppression / top-k ----
        r = T.carte(gauche, "Recherche, suppression, top-k", grille=True)
        r.pack(fill="x")
        ttk.Label(r, text="Moyenne", style="Carte.TLabel").grid(row=1, column=0, sticky="w")
        self.moy = ttk.Entry(r, width=8)
        self.moy.grid(row=1, column=1, sticky="w")
        ttk.Button(r, text="Rechercher", command=self.rechercher).grid(row=1, column=2, padx=3)
        ttk.Button(r, text="Supprimer", command=self.supprimer_moyenne).grid(row=1, column=3)
        ttk.Label(r, text="k", style="Carte.TLabel").grid(row=2, column=0, sticky="w", pady=4)
        self.k = ttk.Spinbox(r, from_=1, to=100000, width=7)
        self.k.set(10)
        self.k.grid(row=2, column=1, sticky="w")
        self.methode = ttk.Combobox(r, values=[NOMS_STRUCTURES[i] for i in range(5)], state="readonly", width=20)
        self.methode.current(2)
        self.methode.grid(row=2, column=2, columnspan=2, sticky="we")
        ttk.Button(r, text="Top-k", command=self.topk).grid(row=3, column=0, columnspan=2, sticky="we", pady=2)
        ttk.Button(r, text="Supprimer la sélection", command=self.supprimer_selection).grid(row=3, column=2, columnspan=2, sticky="we")

        # ---- tableau ----
        haut = ttk.Frame(droite)
        haut.pack(fill="x")
        ttk.Label(haut, text="Affichage :", style="Muet.TLabel").pack(side="left")
        self.ordre = ttk.Combobox(haut, state="readonly", width=34, values=[
            "Moyenne croissante (S2, déjà trié)", "Moyenne croissante (S3, parcours infixe)",
            "Moyenne croissante (S1, copie + tri rapide)", "Ordre d'arrivée (S1)"])
        self.ordre.current(0)
        self.ordre.pack(side="left", padx=6)
        self.limite = ttk.Combobox(haut, state="readonly", width=10, values=["500", "2000", "tous"])
        self.limite.current(0)
        self.limite.pack(side="left")
        ttk.Button(haut, text="Afficher", command=self.remplir).pack(side="left", padx=6)
        self.titre_table = ttk.Label(haut, text="", style="Muet.TLabel")
        self.titre_table.pack(side="left", padx=8)
        cadre = ttk.Frame(droite)
        cadre.pack(fill="both", expand=True, pady=6)
        self.table = ttk.Treeview(cadre, columns=COLONNES, show="headings")
        for c, t, w in zip(COLONNES, ["Matr.", "Nom", "Prénom", "Âge", "Sexe"] + [m[:6] for m in MATIERES] + ["Moyenne"],
                           [60, 120, 100, 45, 45, 60, 60, 60, 60, 60, 75]):
            self.table.heading(c, text=t)
            self.table.column(c, width=w, anchor="center")
        sb = ttk.Scrollbar(cadre, command=self.table.yview)
        self.table.configure(yscrollcommand=sb.set)
        self.table.pack(side="left", fill="both", expand=True)
        sb.pack(side="left", fill="y")
        self.table.bind("<<TreeviewSelect>>", self.details)
        self.detail = T.texte(droite, hauteur=9)
        self.detail.pack(fill="x")

    # ------------------------------------------------------------------ #
    def rafraichir(self):
        self.remplir()

    def base_modifiee(self):
        pass

    def remplir(self, liste=None, titre=None):
        self.table.delete(*self.table.get_children())
        if liste is None:
            o = self.ordre.current()
            liste = (self.b.trie(2) if o == 0 else self.b.trie(3) if o == 1 else
                     self.b.trie(0) if o == 2 else self.b.contenu(0))
            titre = f"{len(liste)} étudiants"
        lim = None if self.limite.get() == "tous" else int(self.limite.get())
        for e in liste[:lim]:
            self.table.insert("", "end", iid=str(e.id), values=(e.id, e.nom, e.prenom, e.age, e.sexe,
                                                                *[f"{x:.2f}" for x in e.notes], f"{e.moyenne:.2f}"))
        if lim and len(liste) > lim:
            titre += f" (les {lim} premiers affichés)"
        self.titre_table.config(text=titre or "")

    def ajouter(self):
        try:
            age = int(self.champs["age"].get())
            notes = [float(e.get().replace(",", ".")) for e in self.notes]
        except ValueError:
            self.msg.config(text="Âge et notes doivent être numériques.", foreground=T.C_SWAP)
            return
        ident, err = self.b.ajouter(self.champs["nom"].get().strip(), self.champs["prenom"].get().strip(),
                                    age, self.sexe.get(), notes)
        if err:
            self.msg.config(text="Erreur : " + err, foreground=T.C_SWAP)
            return
        e = self.b.trouver(ident)
        self.msg.config(text=f"Ajouté : matricule {ident}, moyenne {e.moyenne:.2f}", foreground=T.C_TRIE)
        self.app.maj_statut(f"ajout du matricule {ident}")
        self.app.base_modifiee()
        self.remplir()

    def generer(self):
        try:
            n, graine = int(self.n.get()), int(self.graine.get())
        except ValueError:
            return
        if not 1 <= n <= 200000:
            messagebox.showwarning("Génération", "n doit être entre 1 et 200000.")
            return
        self.config(cursor="watch")
        self.update()
        self.b.generer(n, self.mode.current(), graine)
        self.config(cursor="")
        self.app.maj_statut(f"génération de {n} étudiants ({self.mode.get()})")
        self.app.base_modifiee()
        self.remplir()

    def _cle(self):
        try:
            m = float(self.moy.get().replace(",", "."))
        except ValueError:
            messagebox.showwarning("Moyenne", "Saisir une moyenne entre 0 et 20.")
            return None
        if not 0 <= m <= 20:
            messagebox.showwarning("Moyenne", "La moyenne doit être entre 0 et 20.")
            return None
        return cle_depuis_moyenne(m)

    def rechercher(self):
        cle = self._cle()
        if cle is None:
            return
        self.detail.delete("1.0", "end")
        self.detail.insert("end", f"Recherche de la moyenne {cle / 100:.2f}\n", "titre")
        for s in range(4):
            ex = self.b.rechercher(s, cle)
            c1 = self.b.compteurs()
            nb = self.b.compter(s, cle)
            c2 = self.b.compteurs()
            self.detail.insert("end", f"  {NOMS_STRUCTURES[s]:24} existe : {'oui' if ex else 'non':3}  nombre : {nb:4}"
                                      f"   (recherche {c1['comparaisons']} comparaisons, comptage {c2['comparaisons']})\n")
        trouves = [e for e in self.b.trie(2) if e.cle == cle]
        self.remplir(trouves, f"{len(trouves)} étudiant(s) de moyenne {cle / 100:.2f}")
        self.app.maj_statut(f"recherche de {cle / 100:.2f}")

    def supprimer_moyenne(self):
        cle = self._cle()
        if cle is None:
            return
        self._supprimer(cle, -1)

    def supprimer_selection(self):
        sel = self.table.selection()
        if not sel:
            messagebox.showinfo("Suppression", "Sélectionner un étudiant dans le tableau.")
            return
        e = self.b.trouver(int(sel[0]))
        if e:
            self._supprimer(e.cle, e.id)

    def _supprimer(self, cle, ident):
        e, cas = self.b.supprimer(cle, ident)
        self.detail.delete("1.0", "end")
        if not e:
            self.detail.insert("end", f"Aucun étudiant de moyenne {cle / 100:.2f}.\n", "err")
            return
        from backend import CAS_ABR
        self.detail.insert("end", f"Supprimé des 4 structures : {e.prenom} {e.nom} (matricule {e.id}, "
                                  f"moyenne {e.moyenne:.2f})\nCas de suppression dans l'ABR : "
                                  f"{CAS_ABR.get(cas, '?')}\n", "ok")
        self.app.maj_statut(f"suppression du matricule {e.id}")
        self.app.base_modifiee()
        self.remplir()

    def topk(self):
        try:
            k = int(self.k.get())
        except ValueError:
            return
        meth = self.methode.current()
        liste = self.b.topk(meth, k)
        t, reps = self.b.mesurer(3, meth, k)
        self.remplir(liste, f"Top-{k} par {NOMS_STRUCTURES[meth]} — {t:.2f} µs (clock(), {reps} répétitions)")
        self.app.maj_statut(f"top-{k} ({NOMS_STRUCTURES[meth]})")

    def details(self, _=None):
        sel = self.table.selection()
        if not sel:
            return
        e = self.b.trouver(int(sel[0]))
        if not e:
            return
        d = self.detail
        d.delete("1.0", "end")
        d.insert("end", f"{e.prenom} {e.nom}  —  matricule {e.id}\n", "titre")
        d.insert("end", f"Âge : {e.age}   Sexe : {e.sexe}   Moyenne générale : {e.moyenne:.2f} / 20\n")
        for mat, note in zip(MATIERES, e.notes):
            barre = "█" * int(round(note)) + "·" * (20 - int(round(note)))
            d.insert("end", f"  {mat:14} {note:5.2f}  {barre}\n")
