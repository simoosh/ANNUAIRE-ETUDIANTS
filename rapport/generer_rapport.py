"""
generer_rapport.py — Génère rapport/Rapport_MiniProjet_A.docx à partir des
résultats RÉELS de l'étude expérimentale (resultats/*.csv, graphiques/*.png).

Toutes les valeurs numériques citées dans l'analyse sont lues dans les CSV au
moment de la génération : relancer l'étude puis ce script met le rapport à jour.

Usage : python rapport/generer_rapport.py
"""
import csv
import math
import os
import sys

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(RACINE, "resultats")
GRA = os.path.join(RACINE, "graphiques")
SORTIE = os.path.join(RACINE, "rapport", "Rapport_MiniProjet_A.docx")


# --------------------------------------------------------------------------
# Données
# --------------------------------------------------------------------------
def charger(op):
    with open(os.path.join(RES, f"{op}.csv"), newline="", encoding="utf-8") as f:
        lignes = list(csv.reader(f))
    xs = [int(l[0]) for l in lignes[1:]]
    ser = {s: [float(l[j + 1]) for l in lignes[1:]] for j, s in enumerate(lignes[0][1:])}
    return xs, ser


D = {}


def v(op, serie, i=-1):
    if op not in D:
        D[op] = charger(op)
    return D[op][1][serie][i]


def nmin(op="insertion"):
    if op not in D:
        D[op] = charger(op)
    return D[op][0][0]


def nmax(op="insertion"):
    if op not in D:
        D[op] = charger(op)
    return D[op][0][-1]


def ratio(op, serie):
    return v(op, serie, -1) / v(op, serie, 0)


def pente(op, serie):
    xs, ser = D.setdefault(op, charger(op))
    pts = [(math.log(x), math.log(y)) for x, y in zip(xs, ser[serie]) if y > 0]
    mx = sum(a for a, _ in pts) / len(pts)
    my = sum(b for _, b in pts) / len(pts)
    return sum((a - mx) * (b - my) for a, b in pts) / sum((a - mx) ** 2 for a, _ in pts)


def f(x, chiffres=3):
    """Format français d'un nombre (virgule décimale)."""
    if x >= 100:
        s = f"{x:,.0f}".replace(",", " ")
    else:
        s = f"{x:.{chiffres}g}"
    return s.replace(".", ",")


# --------------------------------------------------------------------------
# Mise en forme
# --------------------------------------------------------------------------
doc = Document()
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(4)
st.paragraph_format.line_spacing = 1.08
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2)
    s.left_margin = s.right_margin = Cm(2.2)
for niv, taille in ((1, 15), (2, 12.5), (3, 11)):
    h = doc.styles[f"Heading {niv}"]
    h.font.name = "Calibri"
    h.font.size = Pt(taille)
    h.font.color.rgb = RGBColor(0x1F, 0x3A, 0x68)


def P(texte, gras=False, italique=False, centre=False, taille=None):
    p = doc.add_paragraph()
    morceaux = texte.split("**")
    for k, m in enumerate(morceaux):
        r = p.add_run(m)
        r.bold = gras or (k % 2 == 1)
        r.italic = italique
        if taille:
            r.font.size = Pt(taille)
    if centre:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def L(items):
    for it in items:
        p = doc.add_paragraph(style="List Bullet")
        morceaux = it.split("**")
        for k, m in enumerate(morceaux):
            p.add_run(m).bold = (k % 2 == 1)
        p.paragraph_format.space_after = Pt(1)


def ombrer(cellule, couleur):
    tc = cellule._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd")
    sh.set(qn("w:val"), "clear")
    sh.set(qn("w:color"), "auto")
    sh.set(qn("w:fill"), couleur)
    tc.append(sh)


def T(entete, lignes, largeurs=None, taille=8.5):
    t = doc.add_table(rows=1, cols=len(entete))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(entete):
        c = t.rows[0].cells[j]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(taille)
        ombrer(c, "D9E2F3")
    for l in lignes:
        cells = t.add_row().cells
        for j, x in enumerate(l):
            cells[j].text = ""
            cells[j].paragraphs[0].add_run(str(x)).font.size = Pt(taille)
    if largeurs:
        for row in t.rows:
            for j, w in enumerate(largeurs):
                row.cells[j].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


FIG = [0]


def FIGS(paires, legende):
    """Une ou deux figures côte à côte, avec légende numérotée."""
    t = doc.add_table(rows=1, cols=len(paires))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    largeur = 16.4 / len(paires)
    for j, nom in enumerate(paires):
        chemin = os.path.join(GRA, nom + ".png")
        p = t.rows[0].cells[j].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if os.path.exists(chemin):
            p.add_run().add_picture(chemin, width=Cm(largeur - 0.2))
        else:
            p.add_run(f"[{nom}.png manquant]")
    FIG[0] += 1
    c = P(f"Figure {FIG[0]} – {legende}", italique=True, centre=True, taille=9)
    c.paragraph_format.space_after = Pt(8)


# --------------------------------------------------------------------------
# Lecture du protocole
# --------------------------------------------------------------------------
proto = {}
with open(os.path.join(RES, "protocole.txt"), encoding="utf-8", errors="replace") as fp:
    for l in fp:
        if ":" in l:
            k, x = l.split(":", 1)
            proto[k.strip()] = x.strip()

N0, N1 = nmin(), nmax()

# ==========================================================================
# PAGE DE TITRE
# ==========================================================================
P("Université Abderrahmane Mira de Béjaïa – Faculté des Sciences Exactes", centre=True, taille=11)
P("Département d'Informatique", centre=True, taille=11)
P("Module : Algorithmique et Complexité — 2ème année Ingénieur — 2026/2027", centre=True, taille=10)
doc.add_paragraph()
P("Mini-projet A", gras=True, centre=True, taille=24)
P("Gestionnaire d'annuaire d'étudiants", gras=True, centre=True, taille=18)
P("Comparaison expérimentale de trois structures de stockage :\nliste non triée, tableau trié, arbre binaire de recherche",
  italique=True, centre=True, taille=12)
doc.add_paragraph()
P("Membres du groupe : ………………………………………………………………", centre=True)
P("Enseignant : ………………………………………", centre=True)
doc.add_paragraph()
T(["Élément", "Contenu"], [
    ["Langage", "C standard (C11) — structures, tris, recherche dichotomique, tas et ABR écrits par le groupe (ni qsort, ni bsearch)"],
    ["Organisation", "16 fichiers .c/.h : un module par structure + tris, tas, mesures, menu, bibliothèque pour l'interface"],
    ["Mesures", f"clock() — {proto.get('Tailles n', '')} — {proto.get('Simulations par taille', '')}"],
    ["Courbes", "gnuplot lancé par system() (31 graphiques, plusieurs courbes par graphe)"],
    ["Bonus", "Tas max pour le top-k ; ABR équilibré ; interface graphique animée (Tkinter + bibliothèque C)"],
], [3.5, 12.5])
doc.add_page_break()

# ==========================================================================
# 1. INTRODUCTION
# ==========================================================================
doc.add_heading("1. Introduction", 1)
P("Une université doit gérer plusieurs milliers d'étudiants, chacun décrit par son nom, son prénom, son âge, "
  "son sexe et ses notes dans cinq matières. La moyenne générale sert de clé de tri et de recherche. "
  "Le but du projet est d'implémenter ce gestionnaire avec trois structures de stockage différentes, puis de "
  "déterminer **expérimentalement** laquelle convient le mieux selon l'opération et la taille de la base, en "
  "confrontant les temps mesurés aux complexités théoriques étudiées en cours (TP1 : complexité expérimentale, "
  "TP2 : tris, TP3 : arbres).")
P("Le livrable comprend : un programme en ligne de commande avec un menu qui résume l'ensemble du travail, un "
  "module d'étude expérimentale qui produit des fichiers CSV et des courbes gnuplot, et une interface graphique "
  "(bonus) qui anime les algorithmes. Toute la partie algorithmique est écrite en C ; l'interface Python ne "
  "fait qu'appeler la bibliothèque C et afficher ses résultats.")

# ==========================================================================
# 2. PROBLÈME
# ==========================================================================
doc.add_heading("2. Présentation du problème", 1)
P("Chaque structure doit offrir les mêmes fonctionnalités :")
L(["ajout d'un étudiant ;",
   "recherche par moyenne : existence, puis nombre d'étudiants ayant cette moyenne ;",
   "suppression d'un étudiant (dans l'ABR : feuille, nœud à un fils, nœud à deux fils) ;",
   "affichage de tous les étudiants par moyenne croissante ;",
   "classement des k meilleurs (S1 : tri du TP2 puis k derniers ; S2 : lecture directe ; S3 : parcours "
   "décroissant arrêté après k étudiants) ;",
   "génération aléatoire (rand()) d'une base de n étudiants."])
P("**Représentation d'un étudiant.** Le type Etudiant contient le nom et le prénom (tableaux de char de taille "
  "fixe 32), l'âge, le sexe ('M'/'F'), les 5 notes, la moyenne et un matricule unique. La moyenne est arrondie "
  "au centième et **également stockée sous forme entière** (champ cle = moyenne × 100, de 0 à 2000). Toutes les "
  "comparaisons portent sur cet entier : elles sont exactes, alors qu'une égalité entre réels float serait "
  "peu fiable. Les saisies sont validées (noms alphabétiques de 1 à 31 caractères, âge de 16 à 80 ans, sexe M/F, "
  "notes dans [0, 20]). sizeof(Etudiant) = 104 octets.")
P("**Conséquence importante : les doublons.** Il n'existe que 2001 moyennes possibles au centième. Les notes "
  "aléatoires étant uniformes sur [0, 20], la moyenne de 5 notes se concentre autour de 10 (écart-type ≈ 2,6). "
  f"Avec n = {N1}, chaque moyenne courante est donc partagée par plusieurs dizaines d'étudiants. Ce phénomène, "
  "réel, influence plusieurs résultats et est discuté dans l'analyse.")

# ==========================================================================
# 3. CHOIX DE CONCEPTION
# ==========================================================================
doc.add_heading("3. Choix de conception", 1)
doc.add_heading("3.1 S1 : tableau dynamique plutôt que liste chaînée", 2)
P("Le sujet laisse le choix entre tableau et liste chaînée pour S1. Nous avons retenu le **tableau dynamique** "
  "(capacité doublée quand il est plein) : ajout en fin en Θ(1) amorti ; accès direct indispensable au tri rapide "
  "(top-k, affichage trié) qui travaille sur une copie contiguë obtenue par memcpy ; mémoire contiguë favorable "
  "au cache, ce qui accélère la recherche séquentielle. Son défaut est la suppression, qui décale les éléments "
  "suivants pour **conserver l'ordre d'arrivée** (définition de S1). Pour mesurer l'effet de ce choix, comme "
  "le demande le sujet, nous avons aussi implémenté la **liste simplement chaînée** (pointeur de queue) et l'avons "
  "incluse dans toutes les mesures (section 7.1).")
doc.add_heading("3.2 S2 : insertion par décalage et double dichotomie", 2)
P("L'ajout réutilise exactement la fonction inserer_dans_trie() du tri par insertion : on part de la fin et on "
  "décale d'une case vers la droite tous les éléments strictement plus grands. La recherche d'existence est une "
  "dichotomie classique qui s'arrête dès que la moyenne est trouvée (meilleur cas Θ(1)). Le comptage utilise deux "
  "dichotomies, borne inférieure et borne supérieure, ce qui donne le nombre de doublons en Θ(log n) sans les "
  "parcourir. La suppression fait une dichotomie puis décale à gauche.")
doc.add_heading("3.3 S3 : politique des moyennes identiques", 2)
P("Nous avons d'abord essayé la politique « clé égale → sous-arbre droit » sur la seule moyenne. Nos tests ont "
  "montré son défaut : les doublons forment des chaînes, et l'ABR « équilibré » de 20 000 étudiants atteignait une "
  "hauteur de 187 au lieu de 15. Nous avons donc retenu la **clé composée (moyenne, matricule)** : l'arbre est "
  "ordonné par la moyenne, et deux moyennes égales sont départagées par le matricule (un étudiant arrivé plus tard "
  "va à droite). Il n'y a jamais deux clés égales : c'est un ABR classique. Conséquences :")
L(["recherche par moyenne : arrêt au premier nœud de cette moyenne, Θ(h) ;",
   "les étudiants de même moyenne forment un intervalle du parcours infixe : le comptage est un parcours "
   "**élagué** (on ne descend à gauche que si la clé du nœud est ≥ à la moyenne cherchée, à droite que si elle "
   "est ≤) en Θ(h + d), d étant le nombre de doublons ;",
   "la construction équilibrée donne la hauteur minimale ⌈log2(n+1)⌉ malgré les doublons ;",
   "un nœud par étudiant : l'arbre a bien n nœuds, et insérer des moyennes triées produit un vrai peigne de "
   "hauteur n (vérifié : hauteur = n pour toutes les tailles) ;",
   "suppression à deux fils : le nœud reçoit les données de son **successeur** (minimum du sous-arbre droit), "
   "puis le successeur, qui n'a pas de fils gauche, est retiré."])
P("**Robustesse.** Un ABR dégénéré de 20 000 nœuds aurait une profondeur de récursion de 20 000 et ferait "
  "déborder la pile. Toutes les opérations de S3 sont donc itératives ou utilisent une pile explicite ; "
  "detruire_arbre() libère les nœuds sans pile, par rotations. Seule la construction équilibrée reste récursive "
  "(profondeur log2 n).")
doc.add_heading("3.4 Organisation du code", 2)
T(["Fichier", "Rôle"], [
    ["etudiant.c/.h", "type Etudiant, moyenne, validation, génération aléatoire (rand())"],
    ["s1_tableau.c/.h, s1_liste.c/.h", "S1 tableau dynamique (retenu) et variante liste chaînée"],
    ["s2_trie.c/.h", "S2 tableau trié (insertion par décalage, dichotomies)"],
    ["s3_abr.c/.h", "S3 ABR : insertion, recherche, comptage, 3 cas de suppression, parcours, ABR équilibré"],
    ["tris.c/.h, tas.c/.h", "tri rapide, tri par insertion ; Entasser, ConstruireTasMax, top-k par tas"],
    ["annuaire.c/.h", "interface commune aux structures ; annuaire contenant les 4 structures synchronisées"],
    ["benchmark.c/.h", "étude expérimentale : chronométrage, CSV, scripts gnuplot, system()"],
    ["main.c", "menu en ligne de commande (16 entrées) et mode --bench"],
    ["memoire.c/.h, instrument.c/.h", "contrôle des fuites et débordements (tests) ; trace pour les animations"],
    ["api.c/.h", "bibliothèque partagée appelée par l'interface graphique (ctypes)"],
], [5.2, 10.8])

# ==========================================================================
# 4. IMPLÉMENTATION
# ==========================================================================
doc.add_heading("4. Détails d'implémentation", 1)
P("**Tri rapide (S1).** Partition de Lomuto avec pivot « médiane de trois » par défaut ; la version classique "
  "(pivot = dernier élément) est conservée pour exhiber le pire cas. La récursion porte sur la plus petite "
  "partie et une boucle traite la plus grande : la profondeur de pile reste O(log n) même dans le pire cas. "
  "L'ordre total (moyenne, matricule) évite la dégradation du tri en présence de nombreuses moyennes égales. "
  "S1 n'est jamais modifié : le tri porte sur une copie.")
P("**Tas max (bonus 1).** Représentation en tableau (fils 2i+1 et 2i+2). Entasser fait descendre un nœud ; "
  "ConstruireTasMax appelle Entasser de n/2 − 1 jusqu'à 0 (Θ(n)) ; chaque extraction échange la racine avec le "
  "dernier élément du tas puis rétablit la propriété (Θ(log n)). Le top-k copie les données de S1, construit le "
  "tas puis fait k extractions : Θ(n + k log n).")
P("**ABR équilibré (bonus 2).** À partir du tableau trié : trouver le milieu m, l'insérer avec inserer_abr(), "
  "puis traiter récursivement [g, m−1] et [m+1, d]. Chaque insertion coûte Θ(log n), d'où Θ(n log n) au total, "
  "et la hauteur obtenue est minimale.")
P("**Mémoire.** Toute allocation est libérée (detruire_arbre(), destruction des listes et tableaux). Le programme "
  "de tests est compilé avec -DSUIVI_MEMOIRE : chaque bloc reçoit un en-tête et une sentinelle de 16 octets, "
  "vérifiée à la libération. Les tests appliquent 4 000 opérations aléatoires aux 4 structures et à un modèle "
  "de référence naïf, vérifient les trois cas de suppression, les doublons, les tris, le tas, l'ABR dégénéré et "
  "l'ABR équilibré : **12 733 vérifications, 0 échec, 0 bloc non libéré, 0 écriture hors bornes**.")
P("**Interface graphique (bonus 3).** Tkinter + matplotlib, reliée à la bibliothèque C (annuaire.dll) par "
  "ctypes. Les fonctions C émettent, quand la trace est activée, des événements élémentaires (comparaison, "
  "échange, décalage, pivot, intervalle de dichotomie, nœud visité, cas de suppression, successeur…). "
  "L'interface rejoue ces événements : les animations reflètent l'exécution réelle du C, avec lecture, pause, "
  "étape suivante, étape précédente, remise à zéro et vitesse réglable. Pour les mesures, le code est compilé "
  "avec -DSANS_INSTRUMENTATION : les macros de trace disparaissent du code mesuré.")

# ==========================================================================
# 5. COMPLEXITÉS THÉORIQUES
# ==========================================================================
doc.add_heading("5. Analyse théorique des complexités", 1)
P("n : nombre d'étudiants ; h : hauteur de l'ABR (≈ log n en moyenne si les insertions sont aléatoires, n dans "
  "le pire cas) ; d : nombre d'étudiants ayant la moyenne cherchée ; k : paramètre du top-k. Format : "
  "meilleur / moyen / pire.")
T(["Opération", "S1 tableau", "S1 liste chaînée", "S2 tableau trié", "S3 ABR"], [
    ["Ajout", "Θ(1) amorti", "Θ(1)", "Θ(1) / Θ(n) / Θ(n)", "Θ(1) / Θ(log n) / Θ(n)"],
    ["Recherche", "Θ(1) / Θ(n) / Θ(n)", "Θ(1) / Θ(n) / Θ(n)", "Θ(1) / Θ(log n) / Θ(log n)", "Θ(1) / Θ(log n) / Θ(n)"],
    ["Comptage", "Θ(n)", "Θ(n)", "Θ(log n)", "Θ(h + d)"],
    ["Suppression", "Θ(n) (recherche + décalages)", "Θ(1) / Θ(n) / Θ(n)", "Θ(log n) / Θ(n) / Θ(n)", "Θ(1) / Θ(log n) / Θ(n)"],
    ["Affichage trié", "Θ(n log n) / Θ(n²) pire", "id. + copie Θ(n)", "Θ(n)", "Θ(n)"],
    ["Top-k", "Θ(n log n) / Θ(n²) pire", "id.", "Θ(k)", "Θ(h + k)"],
    ["Top-k par tas", "Θ(n + k log n)", "—", "—", "—"],
    ["Mémoire", "capacité × 104 o", "n × 112 o", "capacité × 104 o", "n × 120 o"],
], [2.6, 3.4, 3.0, 3.4, 3.6], taille=8)
P("Remarques : la suppression dans le tableau S1 coûte toujours ≈ n opérations, car une position i coûte "
  "i comparaisons plus n − 1 − i décalages ; la liste chaînée n'a pas de décalage, d'où un meilleur cas Θ(1) en "
  "tête. Dans S2, la dichotomie trouve la place d'insertion, mais les décalages restent en Θ(n). Le meilleur "
  "cas du top-k dans S3 est Θ(k) quand le maximum est à la racine (ABR dégénéré à gauche).")

# ==========================================================================
# 6. PROTOCOLE
# ==========================================================================
doc.add_heading("6. Protocole expérimental", 1)
L([f"**Tailles** : n ∈ {{{proto.get('Tailles n', '').replace(' ', ', ')}}} ; "
   f"**{proto.get('Simulations par taille', '').split('(')[0].strip()} simulations** par taille (jeux aléatoires "
   "différents) ; les valeurs présentées sont des moyennes.",
   "**Jeux de données** générés avant toute mesure (la génération n'est jamais chronométrée), identiques pour les "
   "4 structures : aléatoire, croissant (les mêmes étudiants triés par notre tri rapide), décroissant.",
   f"**Chronométrage** avec clock() (CLOCKS_PER_SEC = {proto.get('Horloge', '').split('=')[-1].strip()}, donc une "
   "résolution d'une milliseconde). Les opérations rapides sont répétées par lots (1, 2, 4, 8…) dans une même "
   f"fenêtre chronométrée jusqu'à atteindre **{proto.get('Seuil par mesure', '100 ms').split(' de')[0]}** de temps "
   "cumulé ; temps moyen = temps cumulé / nombre de répétitions (enregistré dans mesures_brutes.csv).",
   "**Opérations destructrices** : pour la suppression, la structure de référence est recopiée (abr_copier, "
   "memcpy) **hors chronométrage** avant chaque répétition, puis n/10 suppressions sont chronométrées et la copie "
   "est détruite hors chronométrage. L'ajout est mesuré par la construction complète (n insertions successives) ; "
   "le temps par insertion est le temps de construction divisé par n.",
   "**Affichage trié** : on mesure la production de la séquence triée dans un tableau, sans printf, pour ne pas "
   "mesurer la vitesse de la console.",
   f"**Compilation** : {proto.get('Options de compilation', '')} ({proto.get('Compilateur', '')}). Aucune trace ni "
   "aucun compteur dans le code mesuré ; l'interface graphique ne participe pas aux mesures (programme séparé).",
   f"Durée totale de l'étude : {proto.get('Duree totale', '')}. Résultats bruts : resultats/mesures_brutes.csv ; "
   "un CSV par opération ; scripts gnuplot dans gnuplot/ ; graphiques PNG dans graphiques/."])
P("**Limites.** La résolution de clock() (1 ms sous Windows) impose les répétitions ; les opérations de quelques "
  "nanosecondes (ajout dans S1) restent proches du coût de la boucle de mesure. Les mesures sont faites sur un "
  "ordinateur multitâche : on observe un bruit de quelques pourcents. Les effets de cache et de l'allocateur "
  "(malloc, realloc) s'ajoutent au modèle théorique, qui compte seulement les opérations élémentaires. Les "
  "courbes « théoriques » sont a·f(n), avec a ajusté par moindres carrés sur les mesures : elles comparent des "
  "**formes de croissance**, pas des valeurs absolues.")

# ==========================================================================
# 7. MEILLEURS / PIRES CAS
# ==========================================================================
doc.add_heading("7. Expériences meilleur cas / pire cas", 1)
T(["Structure", "Opération", "Meilleur cas (jeu)", "Pire cas (jeu)", f"Écart mesuré à n = {N1}"], [
    ["S1 tableau", "recherche", "moyenne du 1er arrivé", "moyenne absente",
     f"{f(v('recherche', 'S1_tableau_pire') / v('recherche', 'S1_tableau_meilleur'))} ×"],
    ["S1 liste", "suppression", "1er arrivé (tête)", "dernier arrivé",
     f"{f(v('suppression', 'S1_liste_fin') / v('suppression', 'S1_liste_debut'))} ×"],
    ["S1 tableau", "affichage trié", "pivot médian de 3", "pivot dernier sur données triées",
     f"{f(v('affichage_trie', 'S1_tableau_pivot_dernier') / v('affichage_trie', 'S1_tableau_croissant'))} ×"],
    ["S2", "ajout", "arrivées croissantes", "arrivées décroissantes",
     f"{f(v('insertion', 'S2_decroissant') / v('insertion', 'S2_croissant'))} ×"],
    ["S2", "recherche", "élément du milieu", "moyenne absente",
     f"{f(v('recherche', 'S2_pire') / v('recherche', 'S2_meilleur'))} ×"],
    ["S2", "suppression", "plus grande moyenne", "plus petite moyenne",
     f"{f(v('suppression', 'S2_debut') / v('suppression', 'S2_fin'))} ×"],
    ["S3", "ajout", "ordre aléatoire / équilibré", "ordre croissant (peigne)",
     f"{f(v('insertion', 'S3_croissant') / v('insertion', 'S3_alea'))} ×"],
    ["S3", "recherche", "ABR équilibré", "ABR dégénéré",
     f"{f(v('recherche', 'S3_degenere_moyen') / v('recherche', 'S3_equilibre_moyen'))} ×"],
    ["S3", "top-k", "max à la racine (décroissant)", "max au fond (croissant)",
     f"{f(v('topk', 'S3_croissant') / v('topk', 'S3_decroissant'))} ×"],
], [2.1, 2.2, 3.7, 4.2, 3.4], taille=8)
P(f"La hauteur de l'ABR confirme que le pire cas est bien atteint : avec des moyennes croissantes ou "
  f"décroissantes, la hauteur vaut exactement n ({f(v('hauteur', 'S3_croissant'))} pour n = {N1}), contre "
  f"{f(v('hauteur', 'S3_alea'))} pour l'ordre aléatoire et {f(v('hauteur', 'S3_equilibre'))} pour la "
  f"construction équilibrée (log2 n = {v('hauteur', 'log2_n'):.2f}).")
FIGS(["s3_hauteur", "s1_tri_pire_cas"], "Hauteur de l'ABR selon l'ordre d'insertion ; pire cas du tri rapide (échelles log).")

# ==========================================================================
# 8. GRAPHES ET INTERPRÉTATION
# ==========================================================================
doc.add_heading("8. Courbes et interprétation", 1)
P("Sur tous les graphes, les traits pleins sont les mesures et les pointillés la complexité théorique ajustée. "
  "Les 31 graphiques produits par gnuplot sont fournis dans graphiques/ ; les plus significatifs sont reproduits "
  "ci-dessous.")

doc.add_heading("8.1 Ajout", 2)
FIGS(["cmp_insertion", "s2_insertion"], "Ajout : comparaison des structures (log) ; S2 meilleur, moyen et pire cas.")
P(f"**S1 est la plus rapide** ({f(v('insertion', 'S1_tableau_alea'))} µs par ajout pour n = {N1}), et son coût "
  "ne dépend pas de n : on ajoute en fin, sans chercher de place. Les petites variations observées viennent des "
  "réallocations (doublement de capacité). La liste chaînée coûte un appel à malloc par étudiant "
  f"({f(v('insertion', 'S1_liste_alea'))} µs). **S3** reste sous la microseconde "
  f"({f(v('insertion', 'S3_alea'))} µs, croissance lente, de type logarithmique), alors que **S2** croît "
  f"linéairement : {f(v('insertion', 'S2_alea', 0))} µs à n = {N0} et {f(v('insertion', 'S2_alea'))} µs à "
  f"n = {N1} (pente log-log {pente('insertion', 'S2_alea'):.2f}). En effet, il faut décaler en moyenne la moitié du "
  "tableau. Les cas extrêmes de S2 sont nets : des arrivées croissantes n'imposent aucun décalage "
  f"({f(v('insertion', 'S2_croissant'))} µs), des arrivées décroissantes décalent tout le tableau "
  f"({f(v('insertion', 'S2_decroissant'))} µs). Pour l'ABR dégénéré, l'ajout coûte "
  f"{f(v('insertion', 'S3_croissant'))} µs : il devient plus lent que S2, car parcourir une chaîne de pointeurs "
  "provoque des défauts de cache, alors que S2 décale une zone contiguë.")

doc.add_heading("8.2 Recherche et comptage", 2)
FIGS(["cmp_recherche", "s3_recherche"], "Recherche par moyenne : comparaison (log) ; S3 selon la forme de l'arbre (log).")
P(f"**S2 et S3 (aléatoire ou équilibré) sont les plus rapides**, avec des temps quasi constants "
  f"({f(v('recherche', 'S2_moyen'))} µs et {f(v('recherche', 'S3_moyen'))} µs à n = {N1}), conformes à Θ(log n) : "
  "multiplier n par 20 n'ajoute qu'environ 4 comparaisons. Dans S1, la recherche d'une moyenne absente parcourt "
  f"toute la liste : {f(v('recherche', 'S1_tableau_pire'))} µs (pente {pente('recherche', 'S1_tableau_pire'):.2f}, "
  "linéaire). La liste chaînée est environ "
  f"{f(v('recherche', 'S1_liste_pire') / v('recherche', 'S1_tableau_pire'))} fois plus lente que le tableau pour "
  "le même nombre de comparaisons : chaque maillon est un accès mémoire dispersé.")
P("**Effet des doublons.** La recherche réussie dans S1 croît moins vite que prévu (pente "
  f"{pente('recherche', 'S1_tableau_moyen'):.2f}). Ce n'est pas une erreur de mesure. Quand une moyenne est "
  "partagée par d étudiants, la première occurrence se trouve en moyenne vers la position n/(d+1). Or d augmente "
  "avec n, puisqu'il n'y a que 2001 moyennes possibles : la position de la première occurrence plafonne autour du "
  "nombre de moyennes distinctes. Le pire cas (moyenne absente) reste, lui, parfaitement linéaire. Pour l'ABR "
  f"dégénéré, la recherche coûte {f(v('recherche', 'S3_degenere_moyen'))} µs, soit "
  f"{f(v('recherche', 'S3_degenere_moyen') / v('recherche', 'S3_equilibre_moyen'))} fois plus que l'ABR équilibré : "
  "c'est une recherche séquentielle dans une liste chaînée.")
P(f"**Comptage** : S2 compte en Θ(log n) ({f(v('comptage', 'S2'))} µs) grâce à ses deux dichotomies ; S1 doit tout "
  f"parcourir ({f(v('comptage', 'S1_tableau'))} µs) ; S3 ({f(v('comptage', 'S3'))} µs) paie Θ(h + d), et d croît "
  "avec n, ce qui explique sa légère croissance.")

doc.add_heading("8.3 Suppression", 2)
FIGS(["s1_suppression", "cmp_suppression"], "Suppression : tableau vs liste chaînée pour S1 ; comparaison des structures (log).")
P(f"**S3 est nettement la plus rapide** ({f(v('suppression', 'S3_moyen'))} µs à n = {N1}). S1 et S2 sont linéaires "
  f"(pentes {pente('suppression', 'S1_tableau_moyen'):.2f} et {pente('suppression', 'S2_moyen'):.2f}) à cause "
  "des décalages. S2 est un peu plus rapide que S1, car sa recherche est dichotomique. **Effet tableau / liste "
  "chaînée** : supprimer le premier arrivé coûte "
  f"{f(v('suppression', 'S1_tableau_debut'))} µs dans le tableau (n − 1 décalages de structures de 104 octets), "
  f"mais seulement {f(v('suppression', 'S1_liste_debut'))} µs dans la liste (aucun décalage). Pour le dernier "
  f"arrivé, c'est l'inverse : la liste ({f(v('suppression', 'S1_liste_fin'))} µs) parcourt tous ses maillons, "
  f"alors que le tableau ({f(v('suppression', 'S1_tableau_fin'))} µs) fait n comparaisons rapides et aucun "
  "décalage. On note qu'un décalage coûte plus cher qu'une comparaison. Dans S2, supprimer la plus grande "
  f"moyenne ({f(v('suppression', 'S2_fin'))} µs) est Θ(log n), supprimer la plus petite "
  f"({f(v('suppression', 'S2_debut'))} µs) décale tout le tableau.")

doc.add_heading("8.4 Affichage trié", 2)
FIGS(["cmp_affichage_trie", "s3_affichage_trie"], "Affichage trié : comparaison (log) ; S3 parcours infixe.")
P(f"**S2 est la plus rapide** ({f(v('affichage_trie', 'S2_alea'))} ms à n = {N1}) : le tableau est déjà trié et il "
  f"suffit de le recopier. Le parcours infixe de S3 ({f(v('affichage_trie', 'S3_alea'))} ms) est aussi linéaire, "
  "mais il suit des pointeurs. S1 doit trier une copie à chaque affichage : "
  f"{f(v('affichage_trie', 'S1_tableau_alea'))} ms, soit Θ(n log n). Avec le pivot « dernier élément » sur des "
  f"données déjà triées, le tri rapide devient quadratique : {f(v('affichage_trie', 'S1_tableau_pivot_dernier'))} ms "
  f"(pente {pente('affichage_trie', 'S1_tableau_pivot_dernier'):.2f}), ce qui justifie le choix de la médiane de "
  "trois.")

doc.add_heading("8.5 Top-k et bonus 1 (tas max)", 2)
FIGS(["bonus_tas_topk", "bonus_tas_topk_k"], "Top-k : quatre méthodes en fonction de n (k = 10) et en fonction de k (n maximal).")
P(f"Pour k = 10 et n = {N1} : S2 lit directement les k derniers ({f(v('topk', 'S2_alea'))} µs, constant) ; S3 "
  f"descend jusqu'au maximum puis remonte k étapes ({f(v('topk', 'S3_alea'))} µs) ; le **tas max** "
  f"({f(v('topk', 'Tas_alea'))} µs) est environ {f(v('topk', 'S1_tableau_alea') / v('topk', 'Tas_alea'))} fois plus "
  f"rapide que le tri rapide complet de S1 ({f(v('topk', 'S1_tableau_alea'))} µs), car ConstruireTasMax coûte Θ(n) "
  "et seules k extractions sont faites, au lieu d'un tri complet en Θ(n log n). En revanche, le tas reste bien "
  "plus lent que S2 et S3, qui disposent déjà d'une structure ordonnée. En fonction de k, l'avantage du tas "
  f"diminue : pour k = {nmax('topk_k')}, le tas ({f(v('topk_k', 'Tas'))} µs) dépasse le tri rapide "
  f"({f(v('topk_k', 'S1_tableau'))} µs), car k log n extractions finissent par coûter plus qu'un tri. Dans S3, le "
  f"top-k dépend de la forme : {f(v('topk', 'S3_decroissant'))} µs quand le maximum est à la racine, "
  f"{f(v('topk', 'S3_croissant'))} µs quand il est au fond d'un peigne.")

doc.add_heading("8.6 Bonus 2 : ABR équilibré", 2)
FIGS(["bonus_abr_construction", "bonus_abr_recherche"], "ABR classique (moyennes croissantes) vs ABR équilibré : construction et recherche (log).")
P(f"Construire l'ABR à partir de {N1} moyennes triées coûte **{f(v('construction', 'S3_croissant'))} ms** avec "
  f"l'insertion classique (Θ(n²), pente {pente('construction', 'S3_croissant'):.2f}), contre "
  f"**{f(v('construction', 'S3_equilibre'))} ms** avec l'insertion du milieu d'abord (Θ(n log n)), soit "
  f"{f(v('construction', 'S3_croissant') / v('construction', 'S3_equilibre'))} fois moins. La hauteur passe de "
  f"{f(v('hauteur', 'S3_croissant'))} à {f(v('hauteur', 'S3_equilibre'))}, et la recherche de "
  f"{f(v('recherche', 'S3_degenere_moyen'))} µs à {f(v('recherche', 'S3_equilibre_moyen'))} µs. L'ABR équilibré "
  "est même un peu meilleur que l'ABR aléatoire (hauteur "
  f"{f(v('hauteur', 'S3_alea'))}) : dans l'ordre aléatoire, les étudiants de même moyenne arrivent par matricule "
  "croissant et forment localement des insertions croissantes, ce qui allonge certaines branches.")

doc.add_heading("8.7 Mémoire", 2)
P(f"À n = {N1} : S1 tableau et S2 occupent {f(v('memoire', 'S1_tableau'))} Ko, car la capacité est doublée et "
  f"peut atteindre 2n ; la liste chaînée occupe {f(v('memoire', 'S1_liste'))} Ko et l'ABR "
  f"{f(v('memoire', 'S3'))} Ko (8 octets de pointeur par maillon, 16 par nœud, mais sans capacité inutilisée). "
  "L'occupation est en Θ(n) pour toutes les structures.")

# ==========================================================================
# 9. SYNTHÈSE
# ==========================================================================
doc.add_heading("9. Tableau de synthèse : complexité théorique / tendance observée", 1)


def tend(op, s):
    a = pente(op, s)
    if a < 0.25:
        t = "constante"
    elif a < 0.75:
        t = "logarithmique"
    elif a < 1.3:
        t = "linéaire"
    elif a < 1.75:
        t = "n log n / surlinéaire"
    else:
        t = "quadratique"
    return f"{t} (α = {a:.2f})"


LIGNES = [
    ("S1 tableau", "Ajout", "Θ(1) amorti", "insertion", "S1_tableau_alea", "ajout en fin ; bruit des réallocations"),
    ("S1 tableau", "Recherche (absente)", "Θ(n)", "recherche", "S1_tableau_pire", "parcours complet"),
    ("S1 tableau", "Recherche (existante)", "Θ(n)", "recherche", "S1_tableau_moyen", "plafonne à cause des doublons"),
    ("S1 tableau", "Suppression", "Θ(n)", "suppression", "S1_tableau_moyen", "recherche + décalages"),
    ("S1 tableau", "Affichage trié", "Θ(n log n)", "affichage_trie", "S1_tableau_alea", "tri rapide d'une copie"),
    ("S1 tableau", "Top-k", "Θ(n log n)", "topk", "S1_tableau_alea", "tri complet puis k derniers"),
    ("S1 liste", "Suppression en tête", "Θ(1)", "suppression", "S1_liste_debut", "pas de décalage"),
    ("S2", "Ajout", "Θ(n)", "insertion", "S2_alea", "décalage de n/2 éléments en moyenne"),
    ("S2", "Ajout (croissant)", "Θ(1)", "insertion", "S2_croissant", "meilleur cas : aucun décalage"),
    ("S2", "Recherche", "Θ(log n)", "recherche", "S2_moyen", "dichotomie"),
    ("S2", "Comptage", "Θ(log n)", "comptage", "S2", "deux dichotomies"),
    ("S2", "Suppression", "Θ(n)", "suppression", "S2_moyen", "décalage à gauche"),
    ("S2", "Affichage trié", "Θ(n)", "affichage_trie", "S2_alea", "déjà trié"),
    ("S2", "Top-k", "Θ(k)", "topk", "S2_alea", "accès direct"),
    ("S3", "Ajout", "Θ(log n)", "insertion", "S3_alea", "descente racine → feuille"),
    ("S3 dégénéré", "Ajout", "Θ(n)", "insertion", "S3_croissant", "peigne de hauteur n"),
    ("S3", "Recherche", "Θ(log n)", "recherche", "S3_moyen", "un chemin racine → feuille"),
    ("S3 dégénéré", "Recherche", "Θ(n)", "recherche", "S3_degenere_moyen", "équivaut à une liste chaînée"),
    ("S3", "Comptage", "Θ(h + d)", "comptage", "S3", "d augmente avec n (doublons)"),
    ("S3", "Suppression", "Θ(log n)", "suppression", "S3_moyen", "recherche + 3 cas en O(1)"),
    ("S3", "Affichage trié", "Θ(n)", "affichage_trie", "S3_alea", "parcours infixe"),
    ("S3", "Top-k", "Θ(log n + k)", "topk", "S3_alea", "infixe inverse arrêté après k"),
    ("Tas max", "Top-k", "Θ(n + k log n)", "topk", "Tas_alea", "ConstruireTasMax + k extractions"),
    ("S3 équilibré", "Construction", "Θ(n log n)", "construction", "S3_equilibre", "milieu d'abord"),
    ("S3 classique", "Construction (triées)", "Θ(n²)", "construction", "S3_croissant", "insertions croissantes"),
]
T(["Structure", "Opération", "Théorie", f"Mesure (n = {N1})", "Tendance observée", "Explication"],
  [(a, b, c, f"{f(v(op, s))} {'ms' if op in ('construction', 'affichage_trie') else 'µs'}", tend(op, s), e)
   for a, b, c, op, s, e in LIGNES], [2.2, 2.6, 2.0, 2.3, 3.2, 4.2], taille=7.5)
P("α est l'exposant empirique (pente de la droite de régression en log-log, T ≈ c·n^α) : α ≈ 0 pour une "
  "opération constante, entre 0 et 0,5 pour log n, ≈ 1 pour n, ≈ 1,1 pour n log n sur cette plage de tailles, "
  "et ≈ 2 pour n². Les écarts observés (accès mémoire dispersés, doublons) sont expliqués dans la section 8.")
P(f"**Écarts au-dessus de la théorie.** Le parcours infixe de S3 (α = {pente('affichage_trie', 'S3_alea'):.2f}) et "
  f"le top-k par tas (α = {pente('topk', 'Tas_alea'):.2f}) sont théoriquement linéaires, mais leur temps croît "
  "plus vite. Le nombre d'opérations est bien proportionnel à n ; c'est le coût de chaque opération qui augmente. "
  "Pour n petit, les données tiennent dans les caches du processeur (L1/L2) ; vers 10 000 étudiants, "
  "l'ensemble de travail (≈ 1 à 2 Mo) dépasse ces caches et chaque accès mémoire dispersé (nœuds de l'ABR, "
  "fils 2i+1 et 2i+2 du tas) devient plus lent. Le modèle théorique, qui attribue un coût constant à chaque "
  "accès, ne voit pas cet effet ; les structures contiguës et parcourues séquentiellement (S2) y échappent.")

# ==========================================================================
# 10. CONCLUSION
# ==========================================================================
doc.add_heading("10. Conclusion", 1)
P("Les mesures confirment les complexités théoriques. Elles montrent aussi des effets que le modèle ne prévoit "
  "pas : la localité mémoire (le tableau bat la liste chaînée à nombre d'opérations égal), et les nombreux "
  "doublons d'une moyenne arrondie au centième. Le choix de la structure dépend de l'usage privilégié :")
L([f"**Si les ajouts dominent** : S1 (tableau). L'ajout est en temps constant "
   f"({f(v('insertion', 'S1_tableau_alea'))} µs) ; S2 est à proscrire ({f(v('insertion', 'S2_alea'))} µs par "
   f"ajout à n = {N1}). Mais toute recherche, tout tri ou tout top-k coûte alors au moins Θ(n).",
   f"**Si les recherches dominent** : S2 ou S3. S2 est la plus régulière (dichotomie garantie Θ(log n), comptage "
   "en Θ(log n)) ; S3 offre le même ordre de grandeur pour la recherche, à condition que l'arbre ne soit pas "
   "dégénéré.",
   f"**Si l'affichage trié ou le top-k dominent** : S2 (copie linéaire, top-k en Θ(k)), puis S3 (parcours infixe). "
   "S1 doit trier à chaque fois ; le tas max réduit ce coût pour un petit k.",
   "**Charge mixte (ajouts, suppressions et recherches)** : S3 est le meilleur compromis (tout en Θ(log n) en "
   f"moyenne, suppression à {f(v('suppression', 'S3_moyen'))} µs contre {f(v('suppression', 'S2_moyen'))} µs "
   "pour S2), à condition d'éviter les insertions triées. Le bonus 2 montre qu'un ABR construit par le milieu "
   "garde une hauteur minimale ; une structure auto-équilibrée (AVL, rouge-noir) le garantirait en permanence."])
P("En résumé : S2 pour une base surtout consultée et rarement modifiée, S3 pour une base dynamique, S1 seulement "
  "pour une collecte en masse suivie de peu de consultations.")

doc.add_heading("Annexe – Reproduire les résultats", 2)
L(["Compilation : build.bat (ou mingw32-make) ; tests : build\\tests.exe",
   "Menu : build\\annuaire.exe ; étude complète : build\\annuaire.exe --bench (ou --bench --rapide)",
   "Graphiques : build\\annuaire.exe --gnuplot ; interface : python gui\\main.py ; rapport : python rapport\\generer_rapport.py"])

doc.save(SORTIE)
print(f"Rapport généré : {SORTIE}")
