"""
backend.py — Liaison ctypes avec la bibliothèque C (build/annuaire.dll).

Ce module ne contient AUCUN algorithme : il convertit simplement les appels
Python en appels aux fonctions C exportées par src/api.c, et les structures C
(Etudiant, EvenementTrace) en objets Python.
"""
import ctypes
import os
import sys
from collections import namedtuple

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TAILLE_NOM = 32
NB_MATIERES = 5
MATIERES = ["Algorithmique", "Analyse", "Algebre", "Architecture", "Anglais"]

# Structures (mêmes valeurs que l'enum de annuaire.h)
S1_TABLEAU, S1_LISTE, S2_TRIE, S3_ABR, TAS = 0, 1, 2, 3, 4
NOMS_STRUCTURES = {
    S1_TABLEAU: "S1 – tableau non trié",
    S1_LISTE: "S1 – liste chaînée",
    S2_TRIE: "S2 – tableau trié",
    S3_ABR: "S3 – ABR",
    TAS: "Tas max (bonus)",
}
GEN_ALEATOIRE, GEN_CROISSANT, GEN_DECROISSANT = 0, 1, 2
CAS_ABR = {0: "feuille", 1: "nœud à un seul fils", 2: "nœud à deux fils (successeur)"}

# Types d'événements de trace (mêmes valeurs que instrument.h)
(EV_COMPARE, EV_SWAP, EV_SHIFT, EV_HOLD, EV_PLACE, EV_PIVOT, EV_RANGE, EV_SORTED,
 EV_DICHO, EV_FOUND, EV_NOTFOUND, EV_NODE_VISIT, EV_NODE_INSERT, EV_DEL_CASE,
 EV_SUCC, EV_NODE_REPLACE, EV_NODE_REMOVE, EV_HEAPIFY, EV_HEAP_SIZE, EV_EXTRACT,
 EV_BUILD_RANGE, EV_COUNT, EV_PHASE) = range(1, 24)


class CEtudiant(ctypes.Structure):
    """Miroir exact du type Etudiant de etudiant.h."""
    _fields_ = [
        ("id", ctypes.c_int),
        ("nom", ctypes.c_char * TAILLE_NOM),
        ("prenom", ctypes.c_char * TAILLE_NOM),
        ("age", ctypes.c_int),
        ("sexe", ctypes.c_char),
        ("notes", ctypes.c_float * NB_MATIERES),
        ("moyenne", ctypes.c_float),
        ("cle", ctypes.c_int),
    ]


class CEvenement(ctypes.Structure):
    _fields_ = [("type", ctypes.c_int), ("a", ctypes.c_int), ("b", ctypes.c_int), ("c", ctypes.c_int)]


Etudiant = namedtuple("Etudiant", "id nom prenom age sexe notes cle moyenne")
Evenement = namedtuple("Evenement", "type a b c")
ArbreExport = namedtuple("ArbreExport", "ids cles fg fd")


def _vers_etudiant(c):
    return Etudiant(c.id, c.nom.decode("utf-8", "replace"), c.prenom.decode("utf-8", "replace"),
                    c.age, c.sexe.decode("ascii", "replace"), [round(x, 2) for x in c.notes],
                    c.cle, c.cle / 100.0)


def cle_depuis_moyenne(m):
    """Moyenne réelle -> clé entière en centièmes (même arrondi que le C)."""
    return int(m * 100.0 + 0.5 + 1e-9)


class BackendErreur(Exception):
    pass


class Backend:
    def __init__(self):
        nom = "annuaire.dll" if sys.platform.startswith("win") else "libannuaire.so"
        chemin = os.path.join(RACINE, "build", nom)
        if not os.path.exists(chemin):
            raise BackendErreur(
                f"Bibliothèque introuvable : {chemin}\n"
                "Compilez d'abord le projet (build.bat ou mingw32-make).")
        self.lib = ctypes.CDLL(chemin)
        self._declarer()
        if self.lib.api_taille_etudiant() != ctypes.sizeof(CEtudiant):
            raise BackendErreur("Incohérence entre la structure Etudiant C et Python.")
        self.lib.api_init()

    # ------------------------------------------------------------------ #
    def _declarer(self):
        L = self.lib
        i, d, v = ctypes.c_int, ctypes.c_double, None
        pi, pd, pll = ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_longlong)
        pe = ctypes.POINTER(CEtudiant)
        sig = {
            "api_version": (i, []), "api_taille_etudiant": (i, []),
            "api_init": (v, []), "api_liberer": (v, []), "api_taille": (i, []),
            "api_generer": (i, [i, i, ctypes.c_uint]),
            "api_ajouter": (i, [ctypes.c_char_p, ctypes.c_char_p, i, ctypes.c_char,
                                ctypes.POINTER(ctypes.c_float), i, pi]),
            "api_message_erreur": (ctypes.c_char_p, [i]),
            "api_supprimer": (i, [i, i, i, pe, pi]),
            "api_rechercher": (i, [i, i, i]), "api_compter": (i, [i, i, i]),
            "api_trie": (i, [i, pe, i]), "api_topk": (i, [i, i, pe, i]),
            "api_contenu": (i, [i, pe]), "api_trouver": (i, [i, pe]),
            "api_memoire": (d, [i]), "api_definir_pivot": (v, [i]),
            "api_abr_stats": (v, [pi, pi, pi, pi, pi, pd]),
            "api_abr_exporter": (i, [pi, pi, pi, pi, i]),
            "api_mesurer": (d, [i, i, i, pll]),
            "api_compteurs": (v, [pll, pll, pll]),
            "api_trace_taille": (i, []), "api_trace_tronquee": (i, []),
            "api_trace_lire": (i, [ctypes.POINTER(CEvenement), i]),
            "api_anim_tri_rapide": (i, [pi, i, i, pi]),
            "api_anim_tri_insertion": (i, [pi, i, pi]),
            "api_anim_dichotomie": (i, [pi, i, i, i, pi]),
            "api_anim_tas": (i, [pi, i, i, pi]),
            "api_anim_abr_vider": (v, []), "api_anim_abr_inserer": (i, [i]),
            "api_anim_abr_sequence": (i, [pi, i, i]),
            "api_anim_abr_rechercher": (i, [i]), "api_anim_abr_compter": (i, [i]),
            "api_anim_abr_supprimer": (i, [i, pi]), "api_anim_abr_topk": (i, [i, pi]),
            "api_anim_abr_exporter": (i, [pi, pi, pi, pi, i]),
            "api_anim_abr_taille": (i, []), "api_anim_abr_hauteur": (i, []),
            "api_bench_abr": (i, [i, ctypes.c_uint, pd, pd, pi, pi]),
        }
        for nom, (res, args) in sig.items():
            f = getattr(L, nom)
            f.restype = res
            f.argtypes = args

    @staticmethod
    def _tab_int(valeurs):
        return (ctypes.c_int * max(1, len(valeurs)))(*valeurs)

    # ------------------------------------------------------------------ #
    # Annuaire principal
    # ------------------------------------------------------------------ #
    def taille(self):
        return self.lib.api_taille()

    def generer(self, n, mode=GEN_ALEATOIRE, graine=2026):
        return bool(self.lib.api_generer(n, mode, graine))

    def ajouter(self, nom, prenom, age, sexe, notes, trace_structure=-1):
        tab = (ctypes.c_float * NB_MATIERES)(*notes)
        ident = ctypes.c_int(0)
        code = self.lib.api_ajouter(nom.encode("utf-8"), prenom.encode("utf-8"), int(age),
                                    sexe.encode("ascii")[:1] or b"?", tab, trace_structure,
                                    ctypes.byref(ident))
        if code != 0:
            msg = self.lib.api_message_erreur(code).decode("utf-8") if code > 0 else "mémoire insuffisante"
            return None, msg
        return ident.value, None

    def supprimer(self, cle, ident=-1, trace_structure=-1):
        e, cas = CEtudiant(), ctypes.c_int(-1)
        ok = self.lib.api_supprimer(cle, ident, trace_structure, ctypes.byref(e), ctypes.byref(cas))
        return (_vers_etudiant(e) if ok else None), cas.value

    def rechercher(self, s, cle, trace=False):
        return bool(self.lib.api_rechercher(s, cle, int(trace)))

    def compter(self, s, cle, trace=False):
        return self.lib.api_compter(s, cle, int(trace))

    def trie(self, s, trace=False):
        n = self.taille()
        buf = (CEtudiant * max(1, n))()
        r = self.lib.api_trie(s, buf, int(trace))
        return [_vers_etudiant(buf[k]) for k in range(max(0, r))]

    def topk(self, methode, k, trace=False):
        buf = (CEtudiant * max(1, k))()
        r = self.lib.api_topk(methode, k, buf, int(trace))
        return [_vers_etudiant(buf[j]) for j in range(max(0, r))]

    def contenu(self, s):
        n = self.taille()
        buf = (CEtudiant * max(1, n))()
        r = self.lib.api_contenu(s, buf)
        return [_vers_etudiant(buf[k]) for k in range(max(0, r))]

    def trouver(self, ident):
        e = CEtudiant()
        return _vers_etudiant(e) if self.lib.api_trouver(ident, ctypes.byref(e)) else None

    def memoire(self, s):
        return self.lib.api_memoire(s)

    def definir_pivot(self, dernier):
        self.lib.api_definir_pivot(1 if dernier else 0)

    def abr_stats(self):
        v = [ctypes.c_int() for _ in range(5)]
        p = ctypes.c_double()
        self.lib.api_abr_stats(*[ctypes.byref(x) for x in v], ctypes.byref(p))
        return dict(hauteur=v[0].value, hg=v[1].value, hd=v[2].value, feuilles=v[3].value,
                    hmin=v[4].value, prof=p.value)

    def _exporter(self, fonction, maxi):
        tabs = [(ctypes.c_int * max(1, maxi))() for _ in range(4)]
        n = fonction(*tabs, maxi)
        return ArbreExport(*[list(t[:n]) for t in tabs])

    def abr_exporter(self, maxi=None):
        return self._exporter(self.lib.api_abr_exporter, maxi or max(1, self.taille()))

    def mesurer(self, op, s, param=0):
        """Temps moyen (µs) mesuré EN C avec clock() : 0 recherche, 1 comptage, 2 tri, 3 top-k."""
        reps = ctypes.c_longlong(0)
        t = self.lib.api_mesurer(op, s, param, ctypes.byref(reps))
        return t, reps.value

    # ------------------------------------------------------------------ #
    # Trace et compteurs de la dernière opération
    # ------------------------------------------------------------------ #
    def compteurs(self):
        c, m, v = ctypes.c_longlong(), ctypes.c_longlong(), ctypes.c_longlong()
        self.lib.api_compteurs(ctypes.byref(c), ctypes.byref(m), ctypes.byref(v))
        return dict(comparaisons=c.value, mouvements=m.value, visites=v.value)

    def trace(self):
        n = self.lib.api_trace_taille()
        buf = (CEvenement * max(1, n))()
        n = self.lib.api_trace_lire(buf, n)
        return [Evenement(buf[k].type, buf[k].a, buf[k].b, buf[k].c) for k in range(n)]

    def trace_tronquee(self):
        return bool(self.lib.api_trace_tronquee())

    # ------------------------------------------------------------------ #
    # Animations (données de démonstration, vraies fonctions C)
    # ------------------------------------------------------------------ #
    def anim_tri_rapide(self, cles, pivot_dernier=False):
        res = (ctypes.c_int * max(1, len(cles)))()
        self.lib.api_anim_tri_rapide(self._tab_int(cles), len(cles), int(pivot_dernier), res)
        return self.trace(), list(res[:len(cles)])

    def anim_tri_insertion(self, cles):
        res = (ctypes.c_int * max(1, len(cles)))()
        self.lib.api_anim_tri_insertion(self._tab_int(cles), len(cles), res)
        return self.trace(), list(res[:len(cles)])

    def anim_dichotomie(self, cles, cle, comptage=False):
        trie = (ctypes.c_int * max(1, len(cles)))()
        r = self.lib.api_anim_dichotomie(self._tab_int(cles), len(cles), cle, int(comptage), trie)
        return self.trace(), list(trie[:len(cles)]), r

    def anim_tas(self, cles, k):
        ext = (ctypes.c_int * max(1, k))()
        r = self.lib.api_anim_tas(self._tab_int(cles), len(cles), k, ext)
        return self.trace(), list(ext[:max(0, r)])

    def anim_abr_vider(self):
        self.lib.api_anim_abr_vider()

    def anim_abr_inserer(self, cle):
        self.lib.api_anim_abr_inserer(cle)
        return self.trace()

    def anim_abr_sequence(self, cles, equilibre=False):
        self.lib.api_anim_abr_sequence(self._tab_int(cles), len(cles), int(equilibre))
        return self.trace()

    def anim_abr_rechercher(self, cle):
        r = self.lib.api_anim_abr_rechercher(cle)
        return self.trace(), r

    def anim_abr_compter(self, cle):
        r = self.lib.api_anim_abr_compter(cle)
        return self.trace(), r

    def anim_abr_supprimer(self, cle):
        cas = ctypes.c_int(-1)
        r = self.lib.api_anim_abr_supprimer(cle, ctypes.byref(cas))
        return self.trace(), bool(r), cas.value

    def anim_abr_topk(self, k):
        out = (ctypes.c_int * max(1, k))()
        r = self.lib.api_anim_abr_topk(k, out)
        return self.trace(), list(out[:max(0, r)])

    def anim_abr_exporter(self):
        return self._exporter(self.lib.api_anim_abr_exporter, max(1, self.lib.api_anim_abr_taille()))

    def anim_abr_hauteur(self):
        return self.lib.api_anim_abr_hauteur()

    def bench_abr(self, n, graine=2026):
        tc, te = ctypes.c_double(), ctypes.c_double()
        hc, he = ctypes.c_int(), ctypes.c_int()
        self.lib.api_bench_abr(n, graine, ctypes.byref(tc), ctypes.byref(te), ctypes.byref(hc), ctypes.byref(he))
        return dict(t_classique=tc.value, t_equilibre=te.value, h_classique=hc.value, h_equilibre=he.value)

    def fermer(self):
        try:
            self.lib.api_liberer()
        except Exception:
            pass
