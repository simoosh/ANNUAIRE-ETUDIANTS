"""Rapports et export : tableau de synthèse, génération du rapport Word, plan de soutenance."""
import csv
import os
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import theme as T
import data
from backend import RACINE
from pages.experiences import ouvrir

DEMO = """PLAN DE DÉMONSTRATION (15 minutes)

 0:00  Tableau de bord : objectif, 3 structures, base synchronisée.
 1:00  Gestion des étudiants : ajout validé (erreur volontaire puis correct),
       génération de 1000 étudiants, recherche + comptage, suppression, top-10.
 3:00  S1 : « Base démo », recherche séquentielle animée, suppression (décalages),
       variante liste chaînée (pas de décalage).
 4:30  S2 : ajout d'une petite moyenne (décalages), dichotomie animée, top-k direct.
 6:00  S3 : insertion, recherche, et les 3 cas de suppression
       (Visualiseur > ABR > « Arbre démo 3 cas »).
 7:30  Visualiseur : tri rapide (pivot, partition), tri par insertion.
 8:30  Bonus 1 : tas max animé (ConstruireTasMax puis extractions) + comparaison.
 9:30  Bonus 2 : ABR classique (peigne) vs équilibré, hauteurs et temps.
10:30  Étude expérimentale : protocole, CSV, graphiques gnuplot (system()).
12:00  Comparaison des complexités : un tableau de bord par structure,
       courbes théoriques ajustées, tableau de synthèse.
13:30  Conclusion : quelle structure selon l'usage (ajouts / recherches / tri).
14:30  Questions.
"""


class PageRapports(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        ttk.Label(self, text="Rapports et export", style="Titre.TLabel").pack(anchor="w")
        barre = ttk.Frame(self, style="Carte.TFrame", padding=8)
        barre.pack(fill="x", pady=6)
        ttk.Button(barre, text="Générer le rapport Word (rapport/)", style="Accent.TButton",
                   command=self.generer).pack(side="left")
        ttk.Button(barre, text="Ouvrir le rapport", command=self.ouvrir_rapport).pack(side="left", padx=4)
        ttk.Button(barre, text="Exporter la synthèse (CSV)", command=self.exporter).pack(side="left", padx=4)
        ttk.Button(barre, text="Dossier rapport/", command=lambda: ouvrir(os.path.join(RACINE, "rapport"))).pack(side="left", padx=4)
        ttk.Button(barre, text="Dossier resultats/", command=lambda: ouvrir(data.DOSSIER_RES)).pack(side="left", padx=4)
        corps = ttk.Frame(self)
        corps.pack(fill="both", expand=True)
        g = T.carte(corps, "Tableau de synthèse : théorie / tendance observée")
        g.pack(side="left", fill="both", expand=True, padx=(0, 6))
        self.table = ttk.Treeview(g, columns=("op", "theo", "val", "tend", "expl"), show="tree headings")
        self.table.heading("#0", text="Structure")
        for c, h, w in (("op", "Opération", 105), ("theo", "Complexité théorique", 120),
                        ("val", "Mesure (n max)", 130), ("tend", "Tendance observée", 190), ("expl", "Explication", 380)):
            self.table.heading(c, text=h)
            self.table.column(c, width=w)
        self.table.column("#0", width=95)
        self.table.pack(fill="both", expand=True)
        d = T.carte(corps, "Démonstration de soutenance")
        d.pack(side="left", fill="y")
        t = T.texte(d, hauteur=30, width=62)
        t.insert("1.0", DEMO)
        t.config(state="disabled")
        t.pack(fill="y", expand=True)

    def rafraichir(self):
        self.table.delete(*self.table.get_children())
        self.lignes = data.tableau_synthese()
        for nom, *v in self.lignes:
            self.table.insert("", "end", text=nom, values=v)

    def exporter(self):
        chemin = filedialog.asksaveasfilename(defaultextension=".csv", initialdir=data.DOSSIER_RES,
                                              initialfile="synthese.csv")
        if chemin:
            with open(chemin, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.writer(f, delimiter=";")
                w.writerow(["Structure", "Opération", "Théorie", "Mesure", "Tendance observée", "Explication"])
                w.writerows(self.lignes)
            self.app.maj_statut("synthèse exportée")

    def generer(self):
        script = os.path.join(RACINE, "rapport", "generer_rapport.py")
        r = subprocess.run([sys.executable, script], cwd=RACINE, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.returncode == 0:
            messagebox.showinfo("Rapport", r.stdout.strip() or "Rapport généré.")
        else:
            messagebox.showerror("Rapport", (r.stdout + r.stderr)[-1500:])

    def ouvrir_rapport(self):
        p = os.path.join(RACINE, "rapport", "Rapport_MiniProjet_A.docx")
        if os.path.exists(p):
            ouvrir(p)
        else:
            messagebox.showinfo("Rapport", "Générer d'abord le rapport.")
