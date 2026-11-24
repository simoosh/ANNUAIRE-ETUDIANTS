"""
frames.py — Conversion de la TRACE émise par le C en images d'animation.

Aucun algorithme n'est réimplémenté ici : on part de l'état initial et on
applique, dans l'ordre, les modifications élémentaires que le code C a
réellement effectuées (échange, décalage, placement, insertion de nœud, ...).
L'état affiché à chaque étape est donc exactement celui du tableau / de
l'arbre C à ce moment de l'exécution.
"""
from backend import (EV_COMPARE, EV_SWAP, EV_SHIFT, EV_HOLD, EV_PLACE, EV_PIVOT, EV_RANGE,
                     EV_SORTED, EV_DICHO, EV_FOUND, EV_NOTFOUND, EV_NODE_VISIT, EV_NODE_INSERT,
                     EV_DEL_CASE, EV_SUCC, EV_NODE_REPLACE, EV_NODE_REMOVE, EV_HEAPIFY,
                     EV_HEAP_SIZE, EV_EXTRACT, EV_BUILD_RANGE, EV_COUNT, EV_PHASE, CAS_ABR)
import theme as T

MAX_IMAGES = 6000


def m(c):
    """Clé (centièmes) -> texte de moyenne."""
    return "—" if c is None else f"{c / 100:.2f}"


# ====================================================================== #
# Tableaux (tris, dichotomie, S1, S2, tas)
# ====================================================================== #
def frames_tableau(initial, evenements, final=None, cle_cherchee=None, titre="État initial"):
    arr = list(initial)
    tries = set()
    etat = dict(rng=None, dicho=None, held=None, heap=None, extraits=[], pivot=None)
    images = []
    stats = dict(cmp=0, ech=0, dec=0)

    def image(roles, msg):
        if len(images) < MAX_IMAGES:
            images.append(dict(arr=list(arr), roles=dict(roles), msg=msg, tries=set(tries),
                               stats=dict(stats), **{k: (list(v) if isinstance(v, list) else v)
                                                      for k, v in etat.items()}))

    image({}, titre)
    for ev in evenements:
        t, a, b, c = ev
        roles = {}
        if etat["pivot"] is not None and etat["pivot"] < len(arr):
            roles[etat["pivot"]] = T.C_PIVOT
        if t == EV_RANGE:
            etat["rng"] = (a, b)
            msg = f"Traitement du sous-tableau [{a} .. {b}]"
        elif t == EV_PIVOT:
            etat["pivot"] = a
            roles[a] = T.C_PIVOT
            msg = f"Pivot = {m(b)} (placé en position {a})"
        elif t == EV_COMPARE:
            stats["cmp"] += 1
            if b == -1:
                roles[a] = T.C_COMPARE
                msg = f"Comparaison de t[{a}] = {m(arr[a])} avec l'élément mis de côté {m(etat['held'])}"
            elif b == -2:
                roles[a] = T.C_COMPARE
                msg = f"Comparaison de t[{a}] = {m(arr[a])} avec la moyenne cherchée {m(cle_cherchee)}"
            else:
                roles[a] = roles[b] = T.C_COMPARE
                if etat["pivot"] == b:
                    roles[b] = T.C_PIVOT
                msg = f"Comparaison t[{a}] = {m(arr[a])}  ↔  t[{b}] = {m(arr[b])}"
        elif t == EV_SWAP:
            stats["ech"] += 1
            arr[a], arr[b] = arr[b], arr[a]
            if etat["pivot"] in (a, b):
                etat["pivot"] = b if etat["pivot"] == a else a
            roles[a] = roles[b] = T.C_SWAP
            msg = f"Échange t[{a}] ↔ t[{b}]"
        elif t == EV_SHIFT:
            stats["dec"] += 1
            while a >= len(arr):
                arr.append(None)
            arr[a] = arr[b]
            roles[a] = T.C_SHIFT
            msg = f"Décalage : t[{a}] ← t[{b}] = {m(arr[a])}"
        elif t == EV_HOLD:
            etat["held"] = b
            while a >= len(arr):
                arr.append(None)
            roles[a] = T.C_PIVOT
            msg = f"Élément à insérer mis de côté : {m(b)}"
        elif t == EV_PLACE:
            while a >= len(arr):
                arr.append(None)
            arr[a] = b
            etat["held"] = None
            roles[a] = T.C_TRIE
            msg = f"Placement de {m(b)} en position {a}"
        elif t == EV_SORTED:
            tries.add(a)
            etat["pivot"] = None
            roles[a] = T.C_TRIE
            msg = f"t[{a}] = {m(arr[a] if a < len(arr) else None)} est à sa place définitive"
        elif t == EV_DICHO:
            etat["dicho"] = (a, b, c)
            stats["cmp"] += 1
            roles[b] = T.C_COMPARE
            msg = f"Intervalle [g={a}, d={c}], milieu m={b} : t[m] = {m(arr[b] if b < len(arr) else None)}"
        elif t == EV_FOUND:
            roles[a] = T.C_TROUVE
            msg = f"Trouvé en position {a} ({m(arr[a] if 0 <= a < len(arr) else None)})"
        elif t == EV_NOTFOUND:
            msg = "Moyenne absente : recherche infructueuse"
        elif t == EV_HEAPIFY:
            etat["heap"] = b
            roles[a] = T.C_PIVOT
            msg = f"Entasser(i = {a}) sur un tas de taille {b}"
        elif t == EV_HEAP_SIZE:
            etat["heap"] = a
            msg = f"Taille du tas = {a}"
        elif t == EV_EXTRACT:
            etat["extraits"].append(a)
            roles[0] = T.C_TROUVE
            msg = f"Extraction du maximum : {m(a)}"
        elif t == EV_COUNT:
            msg = f"Résultat du comptage : {a} étudiant(s)"
        elif t == EV_PHASE:
            msg = "Phase 1 : ConstruireTasMax" if a == 1 else f"Phase 2 : {b} extraction(s) du maximum"
        else:
            continue
        image(roles, msg)
    if final is not None:
        arr = list(final)
        tries = set(range(len(arr))) if final == sorted(final) else tries
        etat["pivot"] = None
        image({}, "État final (lu dans la structure C)")
    return images


# ====================================================================== #
# Arbres binaires de recherche
# ====================================================================== #
def modele_depuis_export(exp):
    """ArbreExport (préfixe + indices des fils) -> (dict id -> [cle, g, d], racine)."""
    mod = {}
    for i, ident in enumerate(exp.ids):
        g = exp.ids[exp.fg[i]] if exp.fg[i] >= 0 else None
        d = exp.ids[exp.fd[i]] if exp.fd[i] >= 0 else None
        mod[ident] = [exp.cles[i], g, d]
    return mod, (exp.ids[0] if exp.ids else None)


def _copie(mod):
    return {k: list(v) for k, v in mod.items()}


def frames_arbre(avant, evenements, apres=None, titre="Arbre initial", cles_cherchee=None,
                 tableau=None):
    """avant / apres : ArbreExport (ou None pour un arbre vide)."""
    mod, rac = modele_depuis_export(avant) if avant else ({}, None)
    cles_ids = cles_depuis_export(avant)
    cles_ids.update(cles_depuis_export(apres))      # clés des nœuds insérés
    images = []
    chemin, trouves, liste = [], set(), []
    etat = dict(info="", rng=None)
    succ = []

    def image(roles, msg):
        if len(images) < MAX_IMAGES:
            images.append(dict(mod=mod, rac=rac, roles=dict(roles), msg=msg, liste=list(liste),
                               rng=etat["rng"], tableau=tableau))

    image({}, titre)
    for ev in evenements:
        t, a, b, c = ev
        roles = {i: T.C_COMPARE for i in chemin}
        roles.update({i: T.C_TROUVE for i in trouves})
        roles.update({i: T.C_SUCC for i in succ})
        if t == EV_NODE_VISIT:
            chemin.append(a)
            roles[a] = T.C_SWAP
            msg = f"Visite du nœud {m(b)}"
            if cles_cherchee is not None:
                msg += (f" : {m(cles_cherchee)} {'<' if cles_cherchee < b else ('>' if cles_cherchee > b else '=')} {m(b)}")
        elif t == EV_FOUND:
            trouves.add(a)
            liste.append(b)
            roles[a] = T.C_TROUVE
            msg = f"Nœud {m(b)} retenu"
        elif t == EV_NOTFOUND:
            msg = "Place vide atteinte : moyenne absente"
        elif t == EV_COUNT:
            msg = f"Comptage terminé : {a} étudiant(s)"
        elif t == EV_NODE_INSERT:
            mod = _copie(mod)
            cle = cles_ids.get(a)
            mod[a] = [cle, None, None]
            if b < 0:
                rac = a
            elif b in mod:
                mod[b][1 + c] = a
            chemin.clear()
            roles = {a: T.C_TRIE}
            msg = f"Insertion de {m(cle)} " + ("à la racine" if b < 0 else f"comme fils {'gauche' if c == 0 else 'droit'} de {m(mod[b][0]) if b in mod else '?'}")
            liste.append(cle)
        elif t == EV_BUILD_RANGE:
            etat["rng"] = (a, b, c)
            chemin.clear()
            msg = f"Sous-tableau [{a} .. {c}] : on insère d'abord le milieu t[{b}]"
        elif t == EV_DEL_CASE:
            roles[b] = T.C_SWAP
            msg = f"Cas de suppression : {CAS_ABR.get(a, '?')}"
        elif t == EV_SUCC:
            succ.append(a)
            roles[a] = T.C_SUCC
            msg = f"Recherche du successeur (minimum du sous-arbre droit) : {m(b)}"
        elif t == EV_NODE_REPLACE:
            mod = _copie(mod)
            if a in mod and b in mod:
                mod[a][0] = mod[b][0]
            roles[a] = T.C_SUCC
            msg = "Le nœud reçoit les données du successeur"
        elif t == EV_NODE_REMOVE:
            if apres is not None:
                mod, rac = modele_depuis_export(apres)
            msg = "Nœud retiré physiquement : le père adopte l'éventuel fils"
            roles = {}
            chemin.clear(); succ.clear()
        else:
            continue
        image(roles, msg)
    if apres is not None:
        mod, rac = modele_depuis_export(apres)
        image({i: T.C_TROUVE for i in trouves if i in mod}, "État final (lu dans l'ABR C)")
    return images


def cles_depuis_export(exp):
    return {i: c for i, c in zip(exp.ids, exp.cles)} if exp else {}
