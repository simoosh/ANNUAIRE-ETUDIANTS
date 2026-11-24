"""
data.py — Lecture des résultats expérimentaux (CSV écrits par le benchmark C)
et éléments d'analyse : ajustement de la courbe théorique, pente empirique,
tableaux de complexité.

Les temps viennent EXCLUSIVEMENT des fichiers CSV produits par le programme C
(build/annuaire --bench). Rien n'est mesuré ni inventé ici.
"""
import csv
import math
import os
from backend import RACINE

DOSSIER_RES = os.path.join(RACINE, "resultats")
DOSSIER_GRAPHES = os.path.join(RACINE, "graphiques")

UNITES = {"insertion": "µs / insertion", "construction": "ms", "recherche": "µs / recherche",
          "comptage": "µs / comptage", "suppression": "µs / suppression", "affichage_trie": "ms",
          "topk": "µs", "topk_k": "µs", "hauteur": "niveaux", "memoire": "Ko"}

THEORIE = {"1": lambda n: 1.0, "logn": lambda n: math.log2(n), "n": lambda n: n,
           "nlogn": lambda n: n * math.log2(n), "n2": lambda n: n * n}
NOM_THEORIE = {"1": "Θ(1)", "logn": "Θ(log n)", "n": "Θ(n)", "nlogn": "Θ(n log n)", "n2": "Θ(n²)"}


def charger(op):
    """Retourne (abscisses, {serie: [valeurs]}) ou (None, None) si absent."""
    chemin = os.path.join(DOSSIER_RES, f"{op}.csv")
    if not os.path.exists(chemin):
        return None, None
    with open(chemin, newline="", encoding="utf-8") as f:
        lignes = list(csv.reader(f))
    if len(lignes) < 2:
        return None, None
    entete = lignes[0]
    xs, series = [], {s: [] for s in entete[1:]}
    for l in lignes[1:]:
        xs.append(int(l[0]))
        for s, v in zip(entete[1:], l[1:]):
            try:
                series[s].append(float(v))
            except ValueError:
                series[s].append(float("nan"))
    return xs, series


def disponible():
    return os.path.exists(os.path.join(DOSSIER_RES, "insertion.csv"))


def ajuster(xs, ys, theorie):
    """a minimisant Σ (y - a f(n))² — courbe théorique mise à l'échelle des mesures."""
    f = THEORIE[theorie]
    num = sum(y * f(x) for x, y in zip(xs, ys) if not math.isnan(y) and x > 1)
    den = sum(f(x) ** 2 for x, y in zip(xs, ys) if not math.isnan(y) and x > 1)
    return num / den if den > 0 else 0.0


def pente(xs, ys):
    """Exposant empirique α (T ≈ c n^α) par régression linéaire en log-log."""
    pts = [(math.log(x), math.log(y)) for x, y in zip(xs, ys) if y and y > 0 and not math.isnan(y)]
    if len(pts) < 2:
        return float("nan")
    mx = sum(p[0] for p in pts) / len(pts)
    my = sum(p[1] for p in pts) / len(pts)
    num = sum((a - mx) * (b - my) for a, b in pts)
    den = sum((a - mx) ** 2 for a, _ in pts)
    return num / den if den else float("nan")


def tendance(alpha):
    if math.isnan(alpha):
        return "—"
    if alpha < 0.25:
        return f"quasi constante (α≈{alpha:.2f})"
    if alpha < 0.75:
        return f"sous-linéaire, type log (α≈{alpha:.2f})"
    if alpha < 1.3:
        return f"linéaire (α≈{alpha:.2f})"
    if alpha < 1.75:
        return f"entre n et n² (α≈{alpha:.2f})"
    return f"quadratique (α≈{alpha:.2f})"


def protocole():
    chemin = os.path.join(DOSSIER_RES, "protocole.txt")
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return f.read()


# --------------------------------------------------------------------------
# Graphes des tableaux de bord : (titre, opération, [(série, légende, théorie)], logy)
# --------------------------------------------------------------------------
TABLEAUX_DE_BORD = {
    "S1": [
        ("Ajout (par insertion)", "insertion", [("S1_tableau_alea", "Tableau", "1"),
                                                ("S1_liste_alea", "Liste chaînée", "1")], False),
        ("Recherche (existence)", "recherche", [("S1_tableau_meilleur", "Meilleur : 1er élément", "1"),
                                                ("S1_tableau_moyen", "Moyen", "n"),
                                                ("S1_tableau_pire", "Pire : absente", "n"),
                                                ("S1_liste_pire", "Liste – pire", "n")], False),
        ("Suppression", "suppression", [("S1_tableau_debut", "Tableau – 1er arrivé", "n"),
                                        ("S1_tableau_fin", "Tableau – dernier", "n"),
                                        ("S1_liste_debut", "Liste – 1er (meilleur)", "1"),
                                        ("S1_liste_fin", "Liste – dernier (pire)", "n")], False),
        ("Affichage trié (tri rapide)", "affichage_trie", [("S1_tableau_alea", "Pivot médian, aléatoire", "nlogn"),
                                                           ("S1_tableau_pivot_dernier", "Pivot dernier, trié (pire)", "n2")], True),
        ("Top-k (k = 10)", "topk", [("S1_tableau_alea", "Tableau", "nlogn"),
                                    ("S1_liste_alea", "Liste chaînée", "nlogn")], False),
        ("Comptage", "comptage", [("S1_tableau", "Tableau", "n"), ("S1_liste", "Liste chaînée", "n")], False),
    ],
    "S2": [
        ("Ajout (insertion triée)", "insertion", [("S2_croissant", "Meilleur : croissant", "1"),
                                                  ("S2_alea", "Moyen : aléatoire", "n"),
                                                  ("S2_decroissant", "Pire : décroissant", "n")], False),
        ("Recherche dichotomique", "recherche", [("S2_meilleur", "Meilleur : milieu", "1"),
                                                 ("S2_moyen", "Moyen", "logn"),
                                                 ("S2_pire", "Pire : absente", "logn")], False),
        ("Suppression", "suppression", [("S2_fin", "Meilleur : plus grande", "logn"),
                                        ("S2_moyen", "Moyen", "n"),
                                        ("S2_debut", "Pire : plus petite", "n")], False),
        ("Affichage trié", "affichage_trie", [("S2_alea", "Parcours", "n")], False),
        ("Top-k (k = 10)", "topk", [("S2_alea", "Lecture directe", "1")], False),
        ("Comptage (2 dichotomies)", "comptage", [("S2", "S2", "logn")], False),
    ],
    "S3": [
        ("Ajout (par insertion)", "insertion", [("S3_alea", "Aléatoire", "logn"),
                                                ("S3_equilibre", "Équilibré", "logn"),
                                                ("S3_croissant", "Croissant (dégénéré)", "n"),
                                                ("S3_decroissant", "Décroissant (dégénéré)", "n")], True),
        ("Recherche", "recherche", [("S3_meilleur", "Meilleur : racine", "1"),
                                    ("S3_moyen", "ABR aléatoire", "logn"),
                                    ("S3_equilibre_moyen", "ABR équilibré", "logn"),
                                    ("S3_degenere_pire", "Dégénéré, absente (pire)", "n")], True),
        ("Suppression", "suppression", [("S3_moyen", "ABR aléatoire", "logn"),
                                        ("S3_degenere_racine", "Dégénéré, racine", "1"),
                                        ("S3_degenere_fond", "Dégénéré, fond (pire)", "n")], True),
        ("Affichage trié (infixe)", "affichage_trie", [("S3_alea", "ABR aléatoire", "n"),
                                                       ("S3_degenere", "ABR dégénéré", "n")], False),
        ("Top-k (infixe inverse)", "topk", [("S3_decroissant", "Max à la racine", "1"),
                                            ("S3_alea", "ABR aléatoire", "logn"),
                                            ("S3_croissant", "Max au fond (pire)", "n")], True),
        ("Hauteur", "hauteur", [("S3_croissant", "Croissant", "n"), ("S3_alea", "Aléatoire", "logn"),
                                ("S3_equilibre", "Équilibré", "logn")], True),
    ],
    "Comparaison": [
        ("Ajout", "insertion", [("S1_tableau_alea", "S1 tableau", None), ("S1_liste_alea", "S1 liste", None),
                                ("S2_alea", "S2", None), ("S3_alea", "S3", None)], True),
        ("Recherche", "recherche", [("S1_tableau_moyen", "S1 tableau", None), ("S1_liste_moyen", "S1 liste", None),
                                    ("S2_moyen", "S2", None), ("S3_moyen", "S3", None)], True),
        ("Suppression", "suppression", [("S1_tableau_moyen", "S1 tableau", None), ("S1_liste_moyen", "S1 liste", None),
                                        ("S2_moyen", "S2", None), ("S3_moyen", "S3", None)], True),
        ("Affichage trié", "affichage_trie", [("S1_tableau_alea", "S1 tableau", None), ("S1_liste_alea", "S1 liste", None),
                                              ("S2_alea", "S2", None), ("S3_alea", "S3", None)], True),
        ("Top-k", "topk", [("S1_tableau_alea", "S1 tableau", None), ("S1_liste_alea", "S1 liste", None),
                           ("S2_alea", "S2", None), ("S3_alea", "S3", None), ("Tas_alea", "Tas max", None)], True),
        ("Mémoire (Ko)", "memoire", [("S1_tableau", "S1 tableau", None), ("S1_liste", "S1 liste", None),
                                     ("S2", "S2", None), ("S3", "S3", None)], False),
    ],
}

# --------------------------------------------------------------------------
# Complexités théoriques : (opération, S1 tableau, S1 liste, S2, S3) — meilleur / moyen / pire
# --------------------------------------------------------------------------
COMPLEXITES = [
    ("Ajout", "Θ(1) amorti", "Θ(1)", "Θ(1) / Θ(n) / Θ(n)", "Θ(1)* / Θ(log n) / Θ(n)"),
    ("Recherche (existence)", "Θ(1) / Θ(n) / Θ(n)", "Θ(1) / Θ(n) / Θ(n)", "Θ(1) / Θ(log n) / Θ(log n)",
     "Θ(1) / Θ(log n) / Θ(n)"),
    ("Comptage d'une moyenne", "Θ(n)", "Θ(n)", "Θ(log n)", "Θ(h + d) : Θ(log n + d) / Θ(n)"),
    ("Suppression", "Θ(n) (recherche + décalages)", "Θ(1) / Θ(n) / Θ(n)", "Θ(log n) / Θ(n) / Θ(n)",
     "Θ(1) / Θ(log n) / Θ(n)"),
    ("Affichage trié", "Θ(n log n) / Θ(n log n) / Θ(n²)", "idem + copie Θ(n)", "Θ(n)", "Θ(n)"),
    ("Top-k", "Θ(n log n) / Θ(n²) au pire", "idem", "Θ(k)", "Θ(h + k) : Θ(k) / Θ(log n + k) / Θ(n)"),
    ("Top-k par tas max (bonus)", "Θ(n + k log n)", "—", "—", "—"),
    ("Mémoire", "≈ capacité × 104 o", "n × 112 o", "≈ capacité × 104 o", "n × 120 o"),
]

EXPLICATIONS = {
    ("S1", "insertion"): "ajout en fin de tableau / en queue de liste, sans recherche de place",
    ("S1", "recherche"): "parcours séquentiel : toute la liste si la moyenne est absente",
    ("S1", "comptage"): "parcours complet obligatoire (doublons possibles n'importe où)",
    ("S1", "suppression"): "tableau : recherche + décalages ≈ n opérations ; liste : pas de décalage",
    ("S1", "affichage_trie"): "copie + tri rapide à chaque affichage (S1 n'est jamais trié)",
    ("S1", "topk"): "tri rapide complet de la copie puis lecture des k derniers",
    ("S2", "insertion"): "dichotomie implicite inutile : il faut décaler en moyenne n/2 éléments",
    ("S2", "recherche"): "dichotomie : l'intervalle est divisé par 2 à chaque comparaison",
    ("S2", "comptage"): "bornes inférieure et supérieure par deux dichotomies",
    ("S2", "suppression"): "dichotomie Θ(log n) puis décalage à gauche Θ(n)",
    ("S2", "affichage_trie"): "tableau déjà trié : simple parcours",
    ("S2", "topk"): "les k derniers éléments sont directement accessibles",
    ("S3", "insertion"): "descente de la racine à une feuille : coût = hauteur ≈ log n si aléatoire",
    ("S3", "recherche"): "un seul chemin racine-feuille ; dégénéré = liste chaînée",
    ("S3", "comptage"): "parcours élagué de l'intervalle des doublons",
    ("S3", "suppression"): "recherche du nœud puis 3 cas (feuille, un fils, deux fils)",
    ("S3", "affichage_trie"): "parcours infixe : chaque nœud visité une fois",
    ("S3", "topk"): "descente jusqu'au maximum puis k étapes de l'infixe inverse",
}

SYNTHESE = [
    ("S1", "S1_tableau", "insertion", "S1_tableau_alea", "Θ(1)"),
    ("S1", "S1_tableau", "recherche", "S1_tableau_moyen", "Θ(n)"),
    ("S1", "S1_tableau", "comptage", "S1_tableau", "Θ(n)"),
    ("S1", "S1_tableau", "suppression", "S1_tableau_moyen", "Θ(n)"),
    ("S1", "S1_tableau", "affichage_trie", "S1_tableau_alea", "Θ(n log n)"),
    ("S1", "S1_tableau", "topk", "S1_tableau_alea", "Θ(n log n)"),
    ("S1", "S1_liste", "suppression", "S1_liste_debut", "Θ(1) (tête)"),
    ("S2", "S2", "insertion", "S2_alea", "Θ(n)"),
    ("S2", "S2", "recherche", "S2_moyen", "Θ(log n)"),
    ("S2", "S2", "comptage", "S2", "Θ(log n)"),
    ("S2", "S2", "suppression", "S2_moyen", "Θ(n)"),
    ("S2", "S2", "affichage_trie", "S2_alea", "Θ(n)"),
    ("S2", "S2", "topk", "S2_alea", "Θ(k)"),
    ("S3", "S3", "insertion", "S3_alea", "Θ(log n)"),
    ("S3", "S3 dégénéré", "insertion", "S3_croissant", "Θ(n)"),
    ("S3", "S3", "recherche", "S3_moyen", "Θ(log n)"),
    ("S3", "S3 dégénéré", "recherche", "S3_degenere_moyen", "Θ(n)"),
    ("S3", "S3", "comptage", "S3", "Θ(log n + d)"),
    ("S3", "S3", "suppression", "S3_moyen", "Θ(log n)"),
    ("S3", "S3", "affichage_trie", "S3_alea", "Θ(n)"),
    ("S3", "S3", "topk", "S3_alea", "Θ(log n + k)"),
    ("Tas", "Tas max", "topk", "Tas_alea", "Θ(n + k log n)"),
]


def tableau_synthese():
    """Lignes : structure, opération, théorie, valeur à n max, tendance observée, explication."""
    lignes = []
    for groupe, nom, op, serie, theo in SYNTHESE:
        xs, ser = charger(op)
        if not xs or serie not in ser:
            continue
        ys = ser[serie]
        a = pente(xs, ys)
        cle = (groupe, op)
        expl = EXPLICATIONS.get(cle, "ConstruireTasMax Θ(n) puis k extractions Θ(log n)")
        if "dégénéré" in nom:
            expl = "insertion de moyennes triées : l'ABR devient un peigne de hauteur n"
        lignes.append((nom, op, theo, f"{ys[-1]:.4g} {UNITES[op]}", tendance(a), expl))
    return lignes
