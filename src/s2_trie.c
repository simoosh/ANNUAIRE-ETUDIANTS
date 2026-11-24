/*
 * s2_trie.c — S2, tableau trié par moyenne croissante.
 */
#include "s2_trie.h"
#include "tris.h"
#include "instrument.h"
#include "memoire.h"
#include <string.h>

void s2_init(S2Tableau *s)
{
    s->t = NULL;
    s->n = 0;
    s->capacite = 0;
}

void s2_detruire(S2Tableau *s)
{
    FREE(s->t);
    s2_init(s);
}

int s2_ajouter(S2Tableau *s, const Etudiant *e)
{
    if (s->n == s->capacite) {
        int nc = s->capacite ? 2 * s->capacite : 16;
        Etudiant *nt = (Etudiant *)REALLOC(s->t, (size_t)nc * sizeof *nt);
        if (!nt) return 0;
        s->t = nt;
        s->capacite = nc;
    }
    inserer_dans_trie(s->t, s->n, e);   /* principe du tri par insertion */
    s->n++;
    return 1;
}

/* Dichotomie classique : s'arrête dès que la clé est trouvée.
 * Meilleur cas Θ(1) (clé au milieu), pire cas Θ(log n) (clé absente). */
int s2_rechercher(const S2Tableau *s, int cle)
{
    int g = 0, d = s->n - 1;
    while (g <= d) {
        int m = g + (d - g) / 2;
        TRACE(EV_DICHO, g, m, d);
        CPT_CMP();
        if (s->t[m].cle == cle) { TRACE(EV_FOUND, m, 0, 0); return m; }
        if (s->t[m].cle < cle) g = m + 1;
        else d = m - 1;
    }
    TRACE(EV_NOTFOUND, g, 0, 0);
    return -1;
}

/* Premier indice i tel que t[i].cle >= cle (n si aucun). Θ(log n). */
int s2_borne_inf(const S2Tableau *s, int cle)
{
    int g = 0, d = s->n;                 /* intervalle [g, d[ */
    while (g < d) {
        int m = g + (d - g) / 2;
        TRACE(EV_DICHO, g, m, d - 1);
        CPT_CMP();
        if (s->t[m].cle < cle) g = m + 1;
        else d = m;
    }
    return g;
}

/* Premier indice i tel que t[i].cle > cle (n si aucun). Θ(log n). */
int s2_borne_sup(const S2Tableau *s, int cle)
{
    int g = 0, d = s->n;
    while (g < d) {
        int m = g + (d - g) / 2;
        TRACE(EV_DICHO, g, m, d - 1);
        CPT_CMP();
        if (s->t[m].cle <= cle) g = m + 1;
        else d = m;
    }
    return g;
}

int s2_compter(const S2Tableau *s, int cle)
{
    int nb = s2_borne_sup(s, cle) - s2_borne_inf(s, cle);
    TRACE(EV_COUNT, nb, 0, 0);
    return nb;
}

int s2_supprimer(S2Tableau *s, int cle, int id, Etudiant *supprime)
{
    int i, pos = s2_borne_inf(s, cle);   /* début du bloc des doublons */
    /* parcours du bloc des étudiants de même moyenne pour trouver le matricule */
    while (pos < s->n && s->t[pos].cle == cle && id >= 0 && s->t[pos].id != id) {
        CPT_CMP();
        pos++;
    }
    if (pos >= s->n || s->t[pos].cle != cle) { TRACE(EV_NOTFOUND, 0, 0, 0); return 0; }
    TRACE(EV_FOUND, pos, 0, 0);
    if (supprime) *supprime = s->t[pos];
    for (i = pos; i < s->n - 1; i++) {   /* décalage à gauche : ordre conservé */
        s->t[i] = s->t[i + 1];
        CPT_MOV();
        TRACE(EV_SHIFT, i, i + 1, 0);
    }
    s->n--;
    return 1;
}

int s2_trie(const S2Tableau *s, Etudiant *sortie)
{
    if (s->n > 0) memcpy(sortie, s->t, (size_t)s->n * sizeof *sortie);
    return s->n;
}

int s2_topk(const S2Tableau *s, int k, Etudiant *sortie)
{
    int i;
    if (k > s->n) k = s->n;
    for (i = 0; i < k; i++) {            /* accès direct aux k derniers */
        sortie[i] = s->t[s->n - 1 - i];
        TRACE(EV_FOUND, s->n - 1 - i, 0, 0);
    }
    return k < 0 ? 0 : k;
}

int s2_copier(S2Tableau *dst, const S2Tableau *src)
{
    s2_init(dst);
    if (src->n == 0) return 1;
    dst->t = (Etudiant *)MALLOC((size_t)src->capacite * sizeof *dst->t);
    if (!dst->t) return 0;
    memcpy(dst->t, src->t, (size_t)src->n * sizeof *dst->t);
    dst->n = src->n;
    dst->capacite = src->capacite;
    return 1;
}

size_t s2_memoire(const S2Tableau *s)
{
    return sizeof *s + (size_t)s->capacite * sizeof(Etudiant);
}
