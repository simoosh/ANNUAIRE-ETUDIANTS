/*
 * tris.c — Tri rapide et tri par insertion (TP2).
 */
#include "tris.h"
#include "instrument.h"

static void echanger(Etudiant *t, int i, int j)
{
    Etudiant tmp;
    if (i == j) return;
    tmp = t[i];
    t[i] = t[j];
    t[j] = tmp;
    CPT_MOV(); CPT_MOV(); CPT_MOV();
    TRACE(EV_SWAP, i, j, 0);
}

/* Comparaison instrumentée de t[i] et t[j] (ordre clé, matricule). */
static int cmp_idx(const Etudiant *t, int i, int j)
{
    CPT_CMP();
    TRACE(EV_COMPARE, i, j, 0);
    return comparer_etudiants(&t[i], &t[j]);
}

/* Partition de Lomuto sur t[g..d] ; le pivot est placé en t[d] puis à sa place
 * définitive, dont l'indice est retourné.
 * Invariant : t[g..i] <= pivot < t[i+1..j-1]. */
static int partition(Etudiant *t, int g, int d, int mode)
{
    int i, j;

    if (mode == PIVOT_MEDIAN3 && d - g >= 2) {
        /* Médiane de trois : on range t[g] <= t[m] puis on amène la médiane en t[d]. */
        int m = g + (d - g) / 2;
        if (cmp_idx(t, m, g) < 0) echanger(t, m, g);
        if (cmp_idx(t, d, g) < 0) echanger(t, d, g);   /* t[g] = min des trois  */
        if (cmp_idx(t, m, d) < 0) echanger(t, m, d);   /* t[d] = médiane        */
    }
    TRACE(EV_PIVOT, d, t[d].cle, t[d].id);

    i = g - 1;
    for (j = g; j < d; j++) {
        if (cmp_idx(t, j, d) <= 0) {
            i++;
            echanger(t, i, j);
        }
    }
    echanger(t, i + 1, d);
    TRACE(EV_SORTED, i + 1, 0, 0);
    return i + 1;
}

static void tri_rapide_rec(Etudiant *t, int g, int d, int mode)
{
    while (g < d) {
        int p;
        TRACE(EV_RANGE, g, d, 0);
        p = partition(t, g, d, mode);
        /* récursion sur la plus petite partie, boucle sur la plus grande */
        if (p - g < d - p) {
            tri_rapide_rec(t, g, p - 1, mode);
            g = p + 1;
        } else {
            tri_rapide_rec(t, p + 1, d, mode);
            d = p - 1;
        }
    }
    if (g == d) TRACE(EV_SORTED, g, 0, 0);
}

void tri_rapide(Etudiant *t, int n, int mode_pivot)
{
    if (n > 1) tri_rapide_rec(t, 0, n - 1, mode_pivot);
    else if (n == 1) TRACE(EV_SORTED, 0, 0, 0);
}

int inserer_dans_trie(Etudiant *t, int n, const Etudiant *x)
{
    int j = n - 1;
    Etudiant cle = *x;                 /* copie : x peut pointer dans t */
    TRACE(EV_HOLD, n, cle.cle, cle.id);
    /* Principe du tri par insertion : on décale vers la droite tant que
     * l'élément de gauche est strictement plus grand. */
    while (j >= 0) {
        CPT_CMP();
        TRACE(EV_COMPARE, j, -1, 0);   /* -1 = élément mis de côté */
        if (comparer_etudiants(&t[j], &cle) <= 0) break;
        t[j + 1] = t[j];
        CPT_MOV();
        TRACE(EV_SHIFT, j + 1, j, 0);
        j--;
    }
    t[j + 1] = cle;
    CPT_MOV();
    TRACE(EV_PLACE, j + 1, cle.cle, cle.id);
    return j + 1;
}

void tri_insertion(Etudiant *t, int n)
{
    int i;
    if (n > 0) TRACE(EV_SORTED, 0, 0, 0);
    for (i = 1; i < n; i++) {
        TRACE(EV_RANGE, 0, i, 0);      /* t[0..i-1] trié, on insère t[i] */
        inserer_dans_trie(t, i, &t[i]);
    }
}

int est_trie(const Etudiant *t, int n)
{
    int i;
    for (i = 1; i < n; i++)
        if (comparer_etudiants(&t[i - 1], &t[i]) > 0) return 0;
    return 1;
}
