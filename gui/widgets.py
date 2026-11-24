"""widgets.py — Composants graphiques : lecteur d'animation, vues tableau / arbre / tas."""
import tkinter as tk
from tkinter import ttk
import theme as T
from frames import m


# ====================================================================== #
# Lecteur : Lecture, Pause, Étape suivante, Étape précédente, Reset, vitesse
# ====================================================================== #
class Lecteur(ttk.Frame):
    def __init__(self, parent, rendu, message=None):
        super().__init__(parent, style="Carte.TFrame", padding=(8, 6))
        self.rendu, self.message = rendu, message
        self.images, self.i, self.joue, self._job = [], 0, False, None
        self.b_reset = ttk.Button(self, text="⏮ Reset", command=self.reset, width=9)
        self.b_prec = ttk.Button(self, text="◀ Préc.", command=self.precedent, width=8)
        self.b_jouer = ttk.Button(self, text="▶ Lecture", command=self.basculer, style="Accent.TButton", width=10)
        self.b_suiv = ttk.Button(self, text="Suiv. ▶", command=self.suivant, width=8)
        self.b_fin = ttk.Button(self, text="⏭ Fin", command=self.fin, width=7)
        for b in (self.b_reset, self.b_prec, self.b_jouer, self.b_suiv, self.b_fin):
            b.pack(side="left", padx=2)
        ttk.Label(self, text="  Vitesse", style="CarteMuet.TLabel").pack(side="left")
        self.vitesse = tk.DoubleVar(value=4.0)
        ttk.Scale(self, from_=0.5, to=40, variable=self.vitesse, length=140).pack(side="left", padx=6)
        self.lbl = ttk.Label(self, text="Étape 0 / 0", style="CarteMuet.TLabel", width=18)
        self.lbl.pack(side="left", padx=8)

    def charger(self, images, jouer=True):
        self.pause()
        self.images, self.i = images, 0
        self._afficher()
        if jouer and len(images) > 1:
            self.basculer()

    def _afficher(self):
        if not self.images:
            self.lbl.config(text="Étape 0 / 0")
            return
        img = self.images[self.i]
        self.rendu(img)
        if self.message:
            self.message(img.get("msg", ""))
        self.lbl.config(text=f"Étape {self.i} / {len(self.images) - 1}")

    def basculer(self):
        if self.joue:
            self.pause()
        else:
            if self.i >= len(self.images) - 1:
                self.i = 0
            self.joue = True
            self.b_jouer.config(text="⏸ Pause")
            self._tic()

    def _tic(self):
        if not self.joue:
            return
        if self.i < len(self.images) - 1:
            self.i += 1
            self._afficher()
            self._job = self.after(int(1000 / max(0.5, self.vitesse.get())), self._tic)
        else:
            self.pause()

    def pause(self):
        self.joue = False
        self.b_jouer.config(text="▶ Lecture")
        if self._job:
            self.after_cancel(self._job)
            self._job = None

    def suivant(self):
        self.pause()
        if self.i < len(self.images) - 1:
            self.i += 1
            self._afficher()

    def precedent(self):
        self.pause()
        if self.i > 0:
            self.i -= 1
            self._afficher()

    def reset(self):
        self.pause()
        self.i = 0
        self._afficher()

    def fin(self):
        self.pause()
        if self.images:
            self.i = len(self.images) - 1
            self._afficher()


# ====================================================================== #
# Vue tableau : barres verticales (tri) ou cases (structures)
# ====================================================================== #
class VueTableau(tk.Canvas):
    def __init__(self, parent, hauteur=300, mode="barres", **kw):
        super().__init__(parent, bg=T.CARTE, highlightthickness=0, height=hauteur, **kw)
        self.mode = mode
        self.img = None
        self.bind("<Configure>", lambda e: self.dessiner(self.img))

    def dessiner(self, img):
        self.img = img
        self.delete("all")
        if not img:
            return
        arr = img["arr"]
        n = len(arr)
        W, H = max(self.winfo_width(), 200), max(self.winfo_height(), 120)
        if n == 0:
            self.create_text(W / 2, H / 2, text="(tableau vide)", fill=T.TEXTE2, font=T.POLICE)
            return
        marge, bas = 20, 42
        larg = (W - 2 * marge) / n
        rng, dicho, tries, roles = img.get("rng"), img.get("dicho"), img.get("tries", set()), img.get("roles", {})
        heap = img.get("heap")
        if rng:
            g, d = rng
            self.create_rectangle(marge + g * larg, 4, marge + (d + 1) * larg, H - bas + 4,
                                  fill=T.C_INTERVALLE, outline=T.BORDURE)
        maxi = max([v for v in arr if v is not None] + [1])
        for i, v in enumerate(arr):
            x0 = marge + i * larg + 1
            x1 = x0 + larg - 2
            coul = T.C_NORMAL
            if i in tries:
                coul = T.C_TRIE
            if heap is not None and i >= heap:
                coul = T.C_TRIE
            if dicho and not (dicho[0] <= i <= dicho[2]):
                coul = T.C_HORS
            coul = roles.get(i, coul)
            if v is None:
                self.create_rectangle(x0, H - bas - 20, x1, H - bas, outline=T.TEXTE2, dash=(2, 2))
                continue
            if self.mode == "barres":
                h = (H - bas - 22) * (v / max(maxi, 1)) + 4
                self.create_rectangle(x0, H - bas - h, x1, H - bas, fill=coul, outline="")
                if larg >= 22:
                    self.create_text((x0 + x1) / 2, H - bas - h - 8, text=m(v), fill=T.TEXTE,
                                     font=("Segoe UI", 8 if larg < 34 else 9))
            else:
                self.create_rectangle(x0, H / 2 - 22, x1, H / 2 + 18, fill=coul, outline=T.BORDURE)
                if larg >= 26:
                    self.create_text((x0 + x1) / 2, H / 2 - 2, text=m(v), fill="white",
                                     font=("Segoe UI", 8 if larg < 40 else 9, "bold"))
            if larg >= 14 or i % 5 == 0:
                self.create_text((x0 + x1) / 2, H - bas + 12, text=str(i), fill=T.TEXTE2, font=("Segoe UI", 7))
        if dicho:
            for lab, j, dy in (("g", dicho[0], 26), ("m", dicho[1], 36), ("d", dicho[2], 26)):
                if 0 <= j < n:
                    self.create_text(marge + (j + 0.5) * larg, H - bas + dy, text=lab, fill=T.C_COMPARE,
                                     font=("Segoe UI", 9, "bold"))
        if img.get("held") is not None:
            self.create_text(W - 10, 14, anchor="e", text=f"élément mis de côté : {m(img['held'])}",
                             fill=T.C_PIVOT, font=T.POLICE_G)
        if img.get("extraits"):
            self.create_text(10, 14, anchor="w", text="extraits : " + ", ".join(m(x) for x in img["extraits"]),
                             fill=T.C_TROUVE, font=T.POLICE)


# ====================================================================== #
# Vue liste chaînée (S1 variante)
# ====================================================================== #
class VueListe(tk.Canvas):
    def __init__(self, parent, hauteur=300, **kw):
        super().__init__(parent, bg=T.CARTE, highlightthickness=0, height=hauteur, **kw)
        self.img = None
        self.bind("<Configure>", lambda e: self.dessiner(self.img))

    def dessiner(self, img):
        self.img = img
        self.delete("all")
        if not img:
            return
        arr, roles = img["arr"], img.get("roles", {})
        W = max(self.winfo_width(), 300)
        bw, bh, gap = 64, 30, 22
        par_ligne = max(1, int((W - 40) // (bw + gap)))
        self.create_text(14, 14, anchor="w", text="tête", fill=T.ACCENT2, font=T.POLICE_P)
        for i, v in enumerate(arr):
            r, c = divmod(i, par_ligne)
            x, y = 20 + c * (bw + gap), 30 + r * (bh + 26)
            coul = roles.get(i, T.C_NORMAL)
            self.create_rectangle(x, y, x + bw - 14, y + bh, fill=coul, outline=T.BORDURE)
            self.create_rectangle(x + bw - 14, y, x + bw, y + bh, fill=T.CARTE2, outline=T.BORDURE)
            self.create_text(x + (bw - 14) / 2, y + bh / 2, text=m(v), fill="white", font=("Segoe UI", 8, "bold"))
            if i < len(arr) - 1:
                if c < par_ligne - 1:
                    self.create_line(x + bw - 7, y + bh / 2, x + bw + gap, y + bh / 2, arrow="last", fill=T.TEXTE2)
                else:
                    self.create_line(x + bw - 7, y + bh, x + bw - 7, y + bh + 12, 20, y + bh + 12, 20, y + bh + 26,
                                     arrow="last", fill=T.TEXTE2)
            else:
                self.create_text(x + bw - 7, y + bh / 2, text="∅", fill=T.TEXTE2)


# ====================================================================== #
# Vue arbre (ABR et tas)
# ====================================================================== #
class VueArbre(ttk.Frame):
    """Canvas défilant ; dessine un modèle {id: [cle, g, d]} à partir de la racine."""

    def __init__(self, parent, hauteur=360, prof_max=8):
        super().__init__(parent, style="Carte.TFrame")
        self.c = tk.Canvas(self, bg=T.CARTE, highlightthickness=0, height=hauteur)
        sx = ttk.Scrollbar(self, orient="horizontal", command=self.c.xview)
        sy = ttk.Scrollbar(self, orient="vertical", command=self.c.yview)
        self.c.configure(xscrollcommand=sx.set, yscrollcommand=sy.set)
        self.c.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.prof_max = prof_max
        self.img = None
        self.c.bind("<Configure>", lambda e: self.dessiner(self.img))

    def dessiner(self, img):
        self.img = img
        c = self.c
        c.delete("all")
        if not img or img.get("rac") is None:
            c.create_text(max(c.winfo_width(), 200) / 2, 60, text="(arbre vide)", fill=T.TEXTE2, font=T.POLICE)
            return
        mod, rac, roles = img["mod"], img["rac"], img.get("roles", {})
        # positions : rang infixe en x, profondeur en y (simple mise en page graphique)
        pos, rang = {}, [0]
        pile, p, prof = [], rac, 1
        while pile or p is not None:
            while p is not None and p in mod:
                pile.append((p, prof))
                p, prof = mod[p][1], prof + 1
            p, prof = pile.pop()
            pos[p] = (rang[0], prof)
            rang[0] += 1
            p, prof = mod[p][2], prof + 1
        n = max(1, rang[0])
        W = max(c.winfo_width(), 300)
        pas = max(30, (W - 40) / n) if n <= 60 else 30
        hmax = max(d for _, d in pos.values())
        dy = 52 if hmax <= 10 else 40
        r = 15 if pas >= 32 else 11
        largeur = 40 + n * pas
        trop = hmax > self.prof_max and n > 80
        for ident, (x, d) in pos.items():
            if trop and d > self.prof_max:
                continue
            X, Y = 20 + x * pas + pas / 2, 24 + (d - 1) * dy
            for f in (mod[ident][1], mod[ident][2]):
                if f is not None and f in pos and not (trop and pos[f][1] > self.prof_max):
                    fx, fd = pos[f]
                    c.create_line(X, Y, 20 + fx * pas + pas / 2, 24 + (fd - 1) * dy, fill=T.BORDURE, width=2)
        for ident, (x, d) in pos.items():
            if trop and d > self.prof_max:
                continue
            X, Y = 20 + x * pas + pas / 2, 24 + (d - 1) * dy
            coul = roles.get(ident, img.get("defaut", {}).get(ident, T.C_NORMAL))
            c.create_oval(X - r, Y - r, X + r, Y + r, fill=coul, outline=T.TEXTE2)
            c.create_text(X, Y, text=m(mod[ident][0]) if r >= 15 else f"{mod[ident][0] // 100}",
                          fill="white", font=("Segoe UI", 7 if r >= 15 else 6, "bold"))
        info = f"{n} nœuds — hauteur {hmax}"
        if trop:
            info += f" (affichage limité à {self.prof_max} niveaux)"
        c.create_text(8, max(c.winfo_height(), 120) - 6, anchor="sw", text=info, fill=T.TEXTE2, font=T.POLICE_P)
        if img.get("liste"):
            c.create_text(W - 8, 8, anchor="ne", text="→ " + ", ".join(m(v) for v in img["liste"][-14:]),
                          fill=T.C_TROUVE, font=T.POLICE_P)
        c.configure(scrollregion=(0, 0, largeur, 40 + hmax * dy))


def modele_tas(arr, taille):
    """Arbre implicite d'un tableau-tas (fils 2i+1, 2i+2) pour l'affichage."""
    mod = {}
    for i, v in enumerate(arr):
        g, d = 2 * i + 1, 2 * i + 2
        mod[i] = [v, g if g < len(arr) else None, d if d < len(arr) else None]
    return mod


class VueTas(ttk.Frame):
    """Tas affiché à la fois comme tableau et comme arbre (même état)."""

    def __init__(self, parent):
        super().__init__(parent, style="Carte.TFrame")
        self.tab = VueTableau(self, hauteur=170)
        self.tab.pack(fill="x")
        self.arbre = VueArbre(self, hauteur=300)
        self.arbre.pack(fill="both", expand=True, pady=(6, 0))

    def dessiner(self, img):
        self.tab.dessiner(img)
        arr = img["arr"]
        taille = img.get("heap") if img.get("heap") is not None else len(arr)
        roles = img.get("roles", {})
        defaut = {i: (T.C_TRIE if i >= taille else T.C_NORMAL) for i in range(len(arr))}
        self.arbre.dessiner(dict(mod=modele_tas(arr, taille), rac=0 if arr else None, roles=roles,
                                 defaut=defaut, liste=img.get("extraits")))


def legende(parent, elements):
    f = ttk.Frame(parent, style="Carte.TFrame")
    for coul, txt in elements:
        tk.Label(f, bg=coul, width=2).pack(side="left", padx=(8, 3))
        ttk.Label(f, text=txt, style="CarteMuet.TLabel").pack(side="left")
    return f
