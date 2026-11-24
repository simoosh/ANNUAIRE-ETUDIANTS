/*
 * tas.c — Tas max et top-k par tas (bonus 1).
 */
#include "tas.h"
#include "instrument.h"
#include "memoire.h"
#include <string.h>

static void echanger(Etudiant *t, int i, int j)
{
    Etudiant tmp = t[i];
    t[i] = t[j];
    t[j] = tmp;
    CPT_MOV(); CPT_MOV(); CPT_MOV();
    TRACE(EV_SWAP, i, j, 0);
}

static int plus_grand(const Etudiant *t, int i, int j)
{
    CPT_CMP();
    TRACE(EV_COMPARE, i, j, 0);
    return comparer_etudiants(&t[i], &t[j]) > 0;
}

void entasser(Etudiant *t, int taille, int i)
{
    int g = 2 * i + 1, d = 2 * i + 2, max = i;
    TRACE(EV_HEAPIFY, i, taille, 0);
    if (g < taille && plus_grand(t, g, max)) max = g;
    if (d < taille && plus_grand(t, d, max)) max = d;
    if (max != i) {
        echanger(t, i, max);
        entasser(t, taille, max);      /* profondeur de récursion <= log2(n) */
    }
}

void construire_tas_max(Etudiant *t, int n)
{
    int i;
    TRACE(EV_PHASE, 1, n, 0);          /* phase 1 : construction */
    TRACE(EV_HEAP_SIZE, n, 0, 0);
    for (i = n / 2 - 1; i >= 0; i--)
        entasser(t, n, i);
}

Etudiant extraire_max(Etudiant *t, int *taille)
{
    Etudiant max = t[0];
    TRACE(EV_EXTRACT, t[0].cle, t[0].id, 0);
    echanger(t, 0, *taille - 1);       /* le max part en fin de tableau */
    (*taille)--;
    TRACE(EV_HEAP_SIZE, *taille, 0, 0);
    if (*taille > 0) entasser(t, *taille, 0);
    return max;
}

int topk_tas(const Etudiant *src, int n, int k, Etudiant *sortie)
{
    Etudiant *t;
    int taille = n, i;
    if (k > n) k = n;
    if (k <= 0) return 0;
    t = (Etudiant *)MALLOC((size_t)n * sizeof *t);
    if (!t) return -1;
    memcpy(t, src, (size_t)n * sizeof *t);   /* la structure source n'est pas modifiée */
    construire_tas_max(t, n);
    TRACE(EV_PHASE, 2, k, 0);                /* phase 2 : k extractions */
    for (i = 0; i < k; i++)
        sortie[i] = extraire_max(t, &taille);
    FREE(t);
    return k;
}

int est_tas_max(const Etudiant *t, int n)
{
    int i;
    for (i = 1; i < n; i++)
        if (comparer_etudiants(&t[(i - 1) / 2], &t[i]) < 0) return 0;
    return 1;
}
