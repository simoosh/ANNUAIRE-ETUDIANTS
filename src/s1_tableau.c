/*
 * s1_tableau.c — S1, liste non triée par tableau dynamique.
 */
#include "s1_tableau.h"
#include "tris.h"
#include "instrument.h"
#include "memoire.h"
#include <string.h>

void s1t_init(S1Tableau *s)
{
    s->t = NULL;
    s->n = 0;
    s->capacite = 0;
}

void s1t_detruire(S1Tableau *s)
{
    FREE(s->t);
    s1t_init(s);
}

int s1t_ajouter(S1Tableau *s, const Etudiant *e)
{
    if (s->n == s->capacite) {               /* doublement : coût amorti Θ(1) */
        int nc = s->capacite ? 2 * s->capacite : 16;
        Etudiant *nt = (Etudiant *)REALLOC(s->t, (size_t)nc * sizeof *nt);
        if (!nt) return 0;
        s->t = nt;
        s->capacite = nc;
    }
    s->t[s->n] = *e;                          /* ajout en fin : ordre d'arrivée */
    CPT_MOV();
    TRACE(EV_PLACE, s->n, e->cle, e->id);
    s->n++;
    return 1;
}

int s1t_rechercher(const S1Tableau *s, int cle)
{
    int i;
    for (i = 0; i < s->n; i++) {             /* recherche séquentielle */
        CPT_CMP();
        TRACE(EV_COMPARE, i, -2, 0);         /* -2 = clé recherchée */
        if (s->t[i].cle == cle) {
            TRACE(EV_FOUND, i, 0, 0);
            return i;
        }
    }
    TRACE(EV_NOTFOUND, 0, 0, 0);
    return -1;
}

int s1t_compter(const S1Tableau *s, int cle)
{
    int i, nb = 0;
    for (i = 0; i < s->n; i++) {             /* parcours complet obligatoire */
        CPT_CMP();
        TRACE(EV_COMPARE, i, -2, 0);
        if (s->t[i].cle == cle) {
            nb++;
            TRACE(EV_FOUND, i, 0, 0);
        }
    }
    TRACE(EV_COUNT, nb, 0, 0);
    return nb;
}

int s1t_supprimer(S1Tableau *s, int cle, int id, Etudiant *supprime)
{
    int i, pos = -1;
    for (i = 0; i < s->n; i++) {
        CPT_CMP();
        TRACE(EV_COMPARE, i, -2, 0);
        if (s->t[i].cle == cle && (id < 0 || s->t[i].id == id)) { pos = i; break; }
    }
    if (pos < 0) { TRACE(EV_NOTFOUND, 0, 0, 0); return 0; }
    TRACE(EV_FOUND, pos, 0, 0);
    if (supprime) *supprime = s->t[pos];
    for (i = pos; i < s->n - 1; i++) {       /* décalage à gauche : ordre conservé */
        s->t[i] = s->t[i + 1];
        CPT_MOV();
        TRACE(EV_SHIFT, i, i + 1, 0);
    }
    s->n--;
    return 1;
}

int s1t_trie(const S1Tableau *s, Etudiant *sortie, int mode_pivot)
{
    if (s->n > 0) memcpy(sortie, s->t, (size_t)s->n * sizeof *sortie);
    tri_rapide(sortie, s->n, mode_pivot);
    return s->n;
}

int s1t_topk(const S1Tableau *s, int k, Etudiant *sortie, int mode_pivot)
{
    Etudiant *copie;
    int i;
    if (k > s->n) k = s->n;
    if (k <= 0) return 0;
    copie = (Etudiant *)MALLOC((size_t)s->n * sizeof *copie);
    if (!copie) return -1;
    memcpy(copie, s->t, (size_t)s->n * sizeof *copie);
    tri_rapide(copie, s->n, mode_pivot);     /* tri du TP2 */
    for (i = 0; i < k; i++)                  /* lecture des k derniers */
        sortie[i] = copie[s->n - 1 - i];
    FREE(copie);
    return k;
}

int s1t_copier(S1Tableau *dst, const S1Tableau *src)
{
    s1t_init(dst);
    if (src->n == 0) return 1;
    dst->t = (Etudiant *)MALLOC((size_t)src->capacite * sizeof *dst->t);
    if (!dst->t) return 0;
    memcpy(dst->t, src->t, (size_t)src->n * sizeof *dst->t);
    dst->n = src->n;
    dst->capacite = src->capacite;
    return 1;
}

size_t s1t_memoire(const S1Tableau *s)
{
    return sizeof *s + (size_t)s->capacite * sizeof(Etudiant);
}
