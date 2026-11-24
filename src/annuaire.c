/*
 * annuaire.c — Interface commune aux structures et gestion de l'annuaire.
 */
#include "annuaire.h"
#include "tris.h"
#include "tas.h"
#include "memoire.h"
#include <string.h>

int g_mode_pivot = PIVOT_MEDIAN3;

const char *structure_nom(int type)
{
    switch (type) {
    case ST_S1_TABLEAU: return "S1 - liste non triee (tableau dynamique)";
    case ST_S1_LISTE:   return "S1 - liste non triee (liste chainee)";
    case ST_S2_TRIE:    return "S2 - tableau trie";
    case ST_S3_ABR:     return "S3 - arbre binaire de recherche";
    case METHODE_TAS:   return "Tas max (bonus)";
    default:            return "?";
    }
}

const char *structure_nom_court(int type)
{
    switch (type) {
    case ST_S1_TABLEAU: return "S1_tableau";
    case ST_S1_LISTE:   return "S1_liste";
    case ST_S2_TRIE:    return "S2";
    case ST_S3_ABR:     return "S3";
    case METHODE_TAS:   return "Tas";
    default:            return "?";
    }
}

void structure_init(Structure *s, int type)
{
    s->type = type;
    switch (type) {
    case ST_S1_TABLEAU: s1t_init(&s->u.s1t); break;
    case ST_S1_LISTE:   s1l_init(&s->u.s1l); break;
    case ST_S2_TRIE:    s2_init(&s->u.s2);   break;
    default:            abr_init(&s->u.s3);  break;
    }
}

void structure_detruire(Structure *s)
{
    switch (s->type) {
    case ST_S1_TABLEAU: s1t_detruire(&s->u.s1t); break;
    case ST_S1_LISTE:   s1l_detruire(&s->u.s1l); break;
    case ST_S2_TRIE:    s2_detruire(&s->u.s2);   break;
    default:            detruire_arbre(&s->u.s3); break;
    }
}

int structure_ajouter(Structure *s, const Etudiant *e)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_ajouter(&s->u.s1t, e);
    case ST_S1_LISTE:   return s1l_ajouter(&s->u.s1l, e);
    case ST_S2_TRIE:    return s2_ajouter(&s->u.s2, e);
    default:            return inserer_abr(&s->u.s3, e);
    }
}

int structure_rechercher(const Structure *s, int cle)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_rechercher(&s->u.s1t, cle) >= 0;
    case ST_S1_LISTE:   return s1l_rechercher(&s->u.s1l, cle) >= 0;
    case ST_S2_TRIE:    return s2_rechercher(&s->u.s2, cle) >= 0;
    default:            return abr_rechercher(&s->u.s3, cle) != NULL;
    }
}

int structure_compter(const Structure *s, int cle)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_compter(&s->u.s1t, cle);
    case ST_S1_LISTE:   return s1l_compter(&s->u.s1l, cle);
    case ST_S2_TRIE:    return s2_compter(&s->u.s2, cle);
    default:            return abr_compter(&s->u.s3, cle);
    }
}

int structure_supprimer(Structure *s, int cle, int id, Etudiant *supprime, int *cas)
{
    if (cas) *cas = -1;
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_supprimer(&s->u.s1t, cle, id, supprime);
    case ST_S1_LISTE:   return s1l_supprimer(&s->u.s1l, cle, id, supprime);
    case ST_S2_TRIE:    return s2_supprimer(&s->u.s2, cle, id, supprime);
    default:            return abr_supprimer(&s->u.s3, cle, id, supprime, cas);
    }
}

int structure_trie(const Structure *s, Etudiant *sortie, int mode_pivot)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_trie(&s->u.s1t, sortie, mode_pivot);
    case ST_S1_LISTE:   return s1l_trie(&s->u.s1l, sortie, mode_pivot);
    case ST_S2_TRIE:    return s2_trie(&s->u.s2, sortie);
    default:            return abr_trie(&s->u.s3, sortie);
    }
}

int structure_topk(const Structure *s, int k, Etudiant *sortie, int mode_pivot)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_topk(&s->u.s1t, k, sortie, mode_pivot);
    case ST_S1_LISTE:   return s1l_topk(&s->u.s1l, k, sortie, mode_pivot);
    case ST_S2_TRIE:    return s2_topk(&s->u.s2, k, sortie);
    default:            return abr_topk(&s->u.s3, k, sortie);
    }
}

int structure_copier(Structure *dst, const Structure *src)
{
    dst->type = src->type;
    switch (src->type) {
    case ST_S1_TABLEAU: return s1t_copier(&dst->u.s1t, &src->u.s1t);
    case ST_S1_LISTE:   return s1l_copier(&dst->u.s1l, &src->u.s1l);
    case ST_S2_TRIE:    return s2_copier(&dst->u.s2, &src->u.s2);
    default:            return abr_copier(&dst->u.s3, &src->u.s3);
    }
}

int structure_taille(const Structure *s)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s->u.s1t.n;
    case ST_S1_LISTE:   return s->u.s1l.n;
    case ST_S2_TRIE:    return s->u.s2.n;
    default:            return s->u.s3.n;
    }
}

size_t structure_memoire(const Structure *s)
{
    switch (s->type) {
    case ST_S1_TABLEAU: return s1t_memoire(&s->u.s1t);
    case ST_S1_LISTE:   return s1l_memoire(&s->u.s1l);
    case ST_S2_TRIE:    return s2_memoire(&s->u.s2);
    default:            return abr_memoire(&s->u.s3);
    }
}

/* Parcours préfixe itératif de l'ABR (ordre interne affiché pour S3). */
static int abr_prefixe(const ABR *a, Etudiant *sortie)
{
    const Noeud **pile;
    int sp = 0, i = 0;
    if (!a->racine) return 0;
    pile = (const Noeud **)MALLOC((size_t)(a->n + 1) * sizeof *pile);
    if (!pile) return -1;
    pile[sp++] = a->racine;
    while (sp > 0) {
        const Noeud *p = pile[--sp];
        sortie[i++] = p->e;
        if (p->droit) pile[sp++] = p->droit;
        if (p->gauche) pile[sp++] = p->gauche;
    }
    FREE(pile);
    return i;
}

int structure_contenu(const Structure *s, Etudiant *sortie)
{
    switch (s->type) {
    case ST_S1_TABLEAU:
        if (s->u.s1t.n) memcpy(sortie, s->u.s1t.t, (size_t)s->u.s1t.n * sizeof *sortie);
        return s->u.s1t.n;
    case ST_S1_LISTE:   return s1l_vers_tableau(&s->u.s1l, sortie);
    case ST_S2_TRIE:    return s2_trie(&s->u.s2, sortie);
    default:            return abr_prefixe(&s->u.s3, sortie);
    }
}

int structure_construire(Structure *s, const Etudiant *t, int n)
{
    int i;
    for (i = 0; i < n; i++)
        if (!structure_ajouter(s, &t[i])) return 0;
    return 1;
}

/* ------------------------------------------------------------------------- */

void annuaire_init(Annuaire *a)
{
    int i;
    for (i = 0; i < NB_STRUCTURES; i++) structure_init(&a->s[i], i);
}

void annuaire_vider(Annuaire *a)
{
    int i;
    for (i = 0; i < NB_STRUCTURES; i++) structure_detruire(&a->s[i]);
    annuaire_init(a);
}

int annuaire_taille(const Annuaire *a)
{
    return structure_taille(&a->s[ST_S1_TABLEAU]);
}

int annuaire_ajouter(Annuaire *a, const Etudiant *e)
{
    int i, ok = 1;
    for (i = 0; i < NB_STRUCTURES; i++) ok &= structure_ajouter(&a->s[i], e);
    return ok;
}

int annuaire_supprimer(Annuaire *a, int cle, int id, Etudiant *supprime)
{
    int i, ok = 1;
    if (id < 0) {
        /* on fixe d'abord QUEL étudiant supprimer (le premier arrivé ayant cette
         * moyenne) pour supprimer le même dans toutes les structures */
        const S1Tableau *s1 = &a->s[ST_S1_TABLEAU].u.s1t;
        int pos = s1t_rechercher(s1, cle);
        if (pos < 0) return 0;
        id = s1->t[pos].id;
    }
    for (i = 0; i < NB_STRUCTURES; i++)
        ok &= structure_supprimer(&a->s[i], cle, id, i == 0 ? supprime : NULL, NULL);
    return ok;
}

int annuaire_topk(const Annuaire *a, int methode, int k, Etudiant *sortie)
{
    if (methode == METHODE_TAS) {
        const S1Tableau *s1 = &a->s[ST_S1_TABLEAU].u.s1t;
        return topk_tas(s1->t, s1->n, k, sortie);
    }
    if (methode < 0 || methode >= NB_STRUCTURES) return 0;
    return structure_topk(&a->s[methode], k, sortie, g_mode_pivot);
}

int annuaire_trouver_id(const Annuaire *a, int id, Etudiant *e)
{
    const S1Tableau *s1 = &a->s[ST_S1_TABLEAU].u.s1t;
    int i;
    for (i = 0; i < s1->n; i++)
        if (s1->t[i].id == id) { *e = s1->t[i]; return 1; }
    return 0;
}

void generer_jeu(Etudiant *t, int n, int mode)
{
    int i;
    for (i = 0; i < n; i++) etudiant_aleatoire(&t[i]);
    if (mode == GEN_CROISSANT || mode == GEN_DECROISSANT) {
        tri_rapide(t, n, PIVOT_MEDIAN3);
        if (mode == GEN_DECROISSANT)
            for (i = 0; i < n / 2; i++) {
                Etudiant tmp = t[i];
                t[i] = t[n - 1 - i];
                t[n - 1 - i] = tmp;
            }
    }
}

int annuaire_generer(Annuaire *a, int n, int mode)
{
    Etudiant *t;
    int i, ok = 1;
    if (n < 0) return 0;
    annuaire_vider(a);
    if (n == 0) return 1;
    t = (Etudiant *)MALLOC((size_t)n * sizeof *t);
    if (!t) return 0;
    generer_jeu(t, n, mode);
    for (i = 0; i < n && ok; i++) ok = annuaire_ajouter(a, &t[i]);
    FREE(t);
    return ok;
}
