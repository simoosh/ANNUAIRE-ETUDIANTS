"""
Étude expérimentale : lance le programme C NON instrumenté (build/annuaire --bench)
dans un processus séparé. L'interface n'intervient pas pendant les mesures ;
elle affiche ensuite les CSV et les graphiques produits par gnuplot (system()).
"""
import os
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import theme as T
import data
from backend import RACINE

EXE = os.path.join(RACINE, "build", "annuaire.exe" if sys.platform.startswith("win") else "annuaire")


def ouvrir(chemin):
    if sys.platform.startswith("win"):
        os.startfile(chemin)
    else:
        subprocess.Popen(["xdg-open", chemin])


class PageExperiences(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.proc = None
        ttk.Label(self, text="Étude expérimentale", style="Titre.TLabel").pack(anchor="w")
        ttk.Label(self, text="Les mesures sont faites par le programme C compilé en -O2 sans instrumentation, "
                             "avec clock(), répétitions jusqu'à un temps cumulé minimal et moyenne sur plusieurs "
                             "simulations. Les courbes sont tracées par gnuplot lancé avec system().",
                  style="Muet.TLabel", wraplength=1100).pack(anchor="w", pady=(0, 8))
        haut = T.carte(self, "Configuration")
        haut.pack(fill="x")
        l = ttk.Frame(haut, style="Carte.TFrame")
        l.pack(fill="x")
        self.mode = tk.StringVar(value="complet")
        ttk.Radiobutton(l, text="Complète (n = 1000 … 20000, 3 simulations, ≈ 5 min)", variable=self.mode,
                        value="complet", style="Carte.TRadiobutton").pack(side="left")
        ttk.Radiobutton(l, text="Rapide (démonstration, ≈ 20 s)", variable=self.mode, value="rapide",
                        style="Carte.TRadiobutton").pack(side="left", padx=10)
        ttk.Radiobutton(l, text="Personnalisée", variable=self.mode, value="perso",
                        style="Carte.TRadiobutton").pack(side="left")
        l2 = ttk.Frame(haut, style="Carte.TFrame")
        l2.pack(fill="x", pady=6)
        ttk.Label(l2, text="Tailles", style="Carte.TLabel").pack(side="left")
        self.tailles = ttk.Entry(l2, width=36)
        self.tailles.insert(0, "1000,2000,5000,10000,15000,20000")
        self.tailles.pack(side="left", padx=4)
        ttk.Label(l2, text="Simulations", style="Carte.TLabel").pack(side="left")
        self.sims = ttk.Spinbox(l2, from_=1, to=10, width=4)
        self.sims.set(3)
        self.sims.pack(side="left", padx=4)
        ttk.Label(l2, text="Seuil (ms)", style="Carte.TLabel").pack(side="left")
        self.seuil = ttk.Spinbox(l2, from_=5, to=1000, width=5)
        self.seuil.set(100)
        self.seuil.pack(side="left", padx=4)
        l3 = ttk.Frame(haut, style="Carte.TFrame")
        l3.pack(fill="x")
        self.b_lancer = ttk.Button(l3, text="▶ Lancer l'étude", style="Accent.TButton", command=self.lancer)
        self.b_lancer.pack(side="left")
        ttk.Button(l3, text="Arrêter", command=self.arreter).pack(side="left", padx=4)
        ttk.Button(l3, text="Relancer gnuplot", command=self.gnuplot).pack(side="left", padx=4)
        ttk.Button(l3, text="Dossier resultats/", command=lambda: ouvrir(data.DOSSIER_RES)).pack(side="left", padx=4)
        ttk.Button(l3, text="Dossier graphiques/", command=lambda: ouvrir(data.DOSSIER_GRAPHES)).pack(side="left", padx=4)
        self.barre = ttk.Progressbar(l3, length=260, mode="determinate")
        self.barre.pack(side="left", padx=12)

        corps = ttk.Frame(self)
        corps.pack(fill="both", expand=True, pady=8)
        g = T.carte(corps, "Journal / protocole")
        g.pack(side="left", fill="both", padx=(0, 6))
        self.journal = T.texte(g, hauteur=30, width=58)
        self.journal.pack(fill="both", expand=True)
        d = T.carte(corps, "Graphiques gnuplot")
        d.pack(side="left", fill="both", expand=True)
        haut_d = ttk.Frame(d, style="Carte.TFrame")
        haut_d.pack(fill="x")
        self.liste = ttk.Combobox(haut_d, state="readonly", width=40)
        self.liste.pack(side="left")
        self.liste.bind("<<ComboboxSelected>>", lambda e: self.afficher_png())
        ttk.Button(haut_d, text="◀", width=3, command=lambda: self.decaler(-1)).pack(side="left", padx=2)
        ttk.Button(haut_d, text="▶", width=3, command=lambda: self.decaler(1)).pack(side="left")
        ttk.Button(haut_d, text="Ouvrir", command=self.ouvrir_png).pack(side="left", padx=4)
        self.image = tk.Label(d, bg=T.CARTE)
        self.image.pack(fill="both", expand=True)
        self._photo = None

    def rafraichir(self):
        self.charger_liste()
        if not self.proc:
            p = data.protocole()
            self.journal.delete("1.0", "end")
            self.journal.insert("end", p if p else "Aucune étude n'a encore été lancée.\n")

    def charger_liste(self):
        if os.path.isdir(data.DOSSIER_GRAPHES):
            pngs = sorted(f for f in os.listdir(data.DOSSIER_GRAPHES) if f.endswith(".png"))
            self.liste["values"] = pngs
            if pngs and not self.liste.get():
                self.liste.current(0)
            self.afficher_png()

    def decaler(self, d):
        v = self.liste["values"]
        if v:
            self.liste.current((self.liste.current() + d) % len(v))
            self.afficher_png()

    def afficher_png(self):
        nom = self.liste.get()
        if not nom:
            return
        try:
            img = tk.PhotoImage(file=os.path.join(data.DOSSIER_GRAPHES, nom))
            larg = max(self.image.winfo_width(), 700)
            f = max(1, -(-img.width() // larg))
            self._photo = img.subsample(f, f) if f > 1 else img
            self.image.config(image=self._photo)
        except tk.TclError:
            pass

    def ouvrir_png(self):
        if self.liste.get():
            ouvrir(os.path.join(data.DOSSIER_GRAPHES, self.liste.get()))

    def lancer(self):
        if self.proc:
            return
        if not os.path.exists(EXE):
            messagebox.showerror("Étude", f"Programme introuvable : {EXE}\nCompiler avec build.bat.")
            return
        args = [EXE, "--bench"]
        if self.mode.get() == "rapide":
            args.append("--rapide")
        elif self.mode.get() == "perso":
            args += ["--tailles", self.tailles.get().replace(" ", ""), "--sims", self.sims.get(), "--seuil", self.seuil.get()]
        self.journal.delete("1.0", "end")
        self.journal.insert("end", "Commande : " + " ".join(os.path.relpath(a, RACINE) if a == EXE else a for a in args) + "\n\n", "titre")
        self.barre["value"] = 0
        self.b_lancer.state(["disabled"])
        kw = {"creationflags": 0x08000000} if sys.platform.startswith("win") else {}
        self.proc = subprocess.Popen(args, cwd=RACINE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, encoding="utf-8", errors="replace", bufsize=1, **kw)
        threading.Thread(target=self._lire, daemon=True).start()

    def _lire(self):
        for ligne in self.proc.stdout:
            self.after(0, self._ligne, ligne)
        code = self.proc.wait()
        self.after(0, self._fin, code)

    def _ligne(self, ligne):
        if ligne.startswith("PROGRESSION"):
            a, b = ligne.split()[1].split("/")
            self.barre["value"] = 100 * int(a) / int(b)
        tag = "titre" if ligne.startswith("---") or ligne.startswith("PROGRESSION") else None
        self.journal.insert("end", ligne, tag)
        self.journal.see("end")

    def _fin(self, code):
        self.proc = None
        self.b_lancer.state(["!disabled"])
        self.journal.insert("end", f"\nTerminé (code {code}).\n", "ok" if code == 0 else "err")
        self.app.maj_statut("étude expérimentale terminée" if code == 0 else "étude interrompue")
        self.liste.set("")
        self.charger_liste()

    def arreter(self):
        if self.proc:
            self.proc.terminate()

    def gnuplot(self):
        r = subprocess.run([EXE, "--gnuplot"], cwd=RACINE, capture_output=True, text=True)
        self.journal.insert("end", r.stdout + r.stderr)
        self.charger_liste()
