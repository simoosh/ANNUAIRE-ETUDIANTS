/*
 * s1_liste.c — S1, liste non triée par liste simplement chaînée.
 */
#include "s1_liste.h"
#include "tris.h"
#include "instrument.h"
#include "memoire.h"

void s1l_init(S1Liste *s)
{
    s->tete = s->queue = NULL;
    s->n = 0;
}

void s1l_detruire(S1Liste *s)
{
    Maillon *m = s->tete;
    while (m) {
        Maillon *suiv = m->suivant;
        FREE(m);
        m = suiv;
    }
    s1l_init(s);
}

int s1l_ajouter(S1Liste *s, const Etudiant *e)
{
    Maillon *m = (Maillon *)MALLOC(sizeof *m);
    if (!m) return 0;
    m->e = *e;
    m->suivant = NULL;
    if (s->queue) s->queue->suivant = m;     /* ajout en queue : ordre d'arrivée */
    else s->tete = m;
    s->queue = m;
    CPT_MOV();
    TRACE(EV_PLACE, s->n, e->cle, e->id);
    s->n++;
    return 1;
}

int s1l_rechercher(const S1Liste *s, int cle)
{
    const Maillon *m;
    int pos = 0;
    for (m = s->tete; m; m = m->suivant, pos++) {
        CPT_CMP(); CPT_VIS();
        TRACE(EV_COMPARE, pos, -2, 0);
        if (m->e.cle == cle) { TRACE(EV_FOUND, pos, 0, 0); return pos; }
    }
    TRACE(EV_NOTFOUND, 0, 0, 0);
    return -1;
}

int s1l_compter(const S1Liste *s, int cle)
{
    const Maillon *m;
    int nb = 0;
    for (m = s->tete; m; m = m->suivant) {
        CPT_CMP(); CPT_VIS();
        if (m->e.cle == cle) nb++;
    }
    TRACE(EV_COUNT, nb, 0, 0);
    return nb;
}

int s1l_supprimer(S1Liste *s, int cle, int id, Etudiant *supprime)
{
    Maillon *prec = NULL, *m = s->tete;
    int pos = 0;
    while (m) {
        CPT_CMP(); CPT_VIS();
        TRACE(EV_COMPARE, pos, -2, 0);
        if (m->e.cle == cle && (id < 0 || m->e.id == id)) break;
        prec = m;
        m = m->suivant;
        pos++;
    }
    if (!m) { TRACE(EV_NOTFOUND, 0, 0, 0); return 0; }
    TRACE(EV_FOUND, pos, 0, 0);
    if (supprime) *supprime = m->e;
    /* chaînage : Θ(1), aucun décalage */
    if (prec) prec->suivant = m->suivant;
    else s->tete = m->suivant;
    if (s->queue == m) s->queue = prec;
    FREE(m);
    s->n--;
    return 1;
}

int s1l_vers_tableau(const S1Liste *s, Etudiant *sortie)
{
    const Maillon *m;
    int i = 0;
    for (m = s->tete; m; m = m->suivant) sortie[i++] = m->e;
    return i;
}

int s1l_trie(const S1Liste *s, Etudiant *sortie, int mode_pivot)
{
    s1l_vers_tableau(s, sortie);             /* pas d'accès direct : recopie */
    tri_rapide(sortie, s->n, mode_pivot);
    return s->n;
}

int s1l_topk(const S1Liste *s, int k, Etudiant *sortie, int mode_pivot)
{
    Etudiant *copie;
    int i;
    if (k > s->n) k = s->n;
    if (k <= 0) return 0;
    copie = (Etudiant *)MALLOC((size_t)s->n * sizeof *copie);
    if (!copie) return -1;
    s1l_vers_tableau(s, copie);
    tri_rapide(copie, s->n, mode_pivot);
    for (i = 0; i < k; i++) sortie[i] = copie[s->n - 1 - i];
    FREE(copie);
    return k;
}

int s1l_copier(S1Liste *dst, const S1Liste *src)
{
    const Maillon *m;
    s1l_init(dst);
    for (m = src->tete; m; m = m->suivant)
        if (!s1l_ajouter(dst, &m->e)) { s1l_detruire(dst); return 0; }
    return 1;
}

size_t s1l_memoire(const S1Liste *s)
{
    return sizeof *s + (size_t)s->n * sizeof(Maillon);
}
