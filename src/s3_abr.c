/*
 * s3_abr.c — S3, arbre binaire de recherche indexé sur la moyenne.
 */
#include "s3_abr.h"
#include "instrument.h"
#include "memoire.h"
#include <math.h>

/* ------------------------------------------------------------------------- */
/* Pile explicite (remplace la récursion). Les 64 premières entrées sont sur  */
/* la pile d'exécution : aucune allocation pour un arbre de hauteur <= 64.    */
/* ------------------------------------------------------------------------- */
typedef struct {
    const Noeud *noeud;
    Noeud **place;      /* abr_copier : où brancher la copie */
    int prof;           /* profondeur (hauteur, statistiques) */
    int parent, cote;   /* abr_exporter */
} Entree;

typedef struct {
    Entree *t;
    int n, cap;
    Entree local[64];
    int erreur;
} Pile;

static void pile_init(Pile *p) { p->t = p->local; p->n = 0; p->cap = 64; p->erreur = 0; }

static void pile_liberer(Pile *p) { if (p->t != p->local) FREE(p->t); pile_init(p); }

static int pile_empiler(Pile *p, Entree e)
{
    if (p->n == p->cap) {
        int nc = 2 * p->cap, i;
        Entree *nt;
        if (p->t == p->local) {
            nt = (Entree *)MALLOC((size_t)nc * sizeof *nt);
            if (nt) for (i = 0; i < p->n; i++) nt[i] = p->local[i];
        } else {
            nt = (Entree *)REALLOC(p->t, (size_t)nc * sizeof *nt);
        }
        if (!nt) { p->erreur = 1; return 0; }
        p->t = nt;
        p->cap = nc;
    }
    p->t[p->n++] = e;
    return 1;
}

static Entree entree(const Noeud *n, int prof)
{
    Entree e;
    e.noeud = n; e.place = NULL; e.prof = prof; e.parent = -1; e.cote = 0;
    return e;
}

/* ------------------------------------------------------------------------- */

void abr_init(ABR *a)
{
    a->racine = NULL;
    a->n = 0;
}

/* Destruction sans pile ni récursion : on « fait tourner » à droite tant que la
 * racine a un fils gauche, sinon on libère la racine et on passe à droite.
 * Chaque nœud est traité un nombre constant de fois : Θ(n). */
void detruire_arbre(ABR *a)
{
    Noeud *r = a->racine;
    while (r) {
        if (r->gauche) {
            Noeud *g = r->gauche;
            r->gauche = g->droit;
            g->droit = r;
            r = g;
        } else {
            Noeud *d = r->droit;
            FREE(r);
            r = d;
        }
    }
    abr_init(a);
}

int inserer_abr(ABR *a, const Etudiant *e)
{
    Noeud *nouveau, *pere = NULL, **place = &a->racine;
    int cote = 0;   /* côté de branchement, utilisé par la trace */
    while (*place) {                           /* descente jusqu'à une place vide */
        pere = *place;
        CPT_CMP(); CPT_VIS();
        TRACE(EV_NODE_VISIT, pere->e.id, pere->e.cle, 0);
        /* clé composée (moyenne, matricule) : jamais d'égalité */
        if (comparer_etudiants(e, &pere->e) < 0) { place = &pere->gauche; cote = 0; }
        else                                     { place = &pere->droit;  cote = 1; }
    }
    nouveau = (Noeud *)MALLOC(sizeof *nouveau);
    if (!nouveau) return 0;
    nouveau->e = *e;
    nouveau->gauche = nouveau->droit = NULL;
    *place = nouveau;
    a->n++;
    TRACE(EV_NODE_INSERT, e->id, pere ? pere->e.id : -1, cote);
    (void)cote;                                /* inutilisé sans instrumentation */
    return 1;
}

const Noeud *abr_rechercher(const ABR *a, int cle)
{
    const Noeud *p = a->racine;
    while (p) {
        CPT_CMP(); CPT_VIS();
        TRACE(EV_NODE_VISIT, p->e.id, p->e.cle, 0);
        if (cle == p->e.cle) { TRACE(EV_FOUND, p->e.id, p->e.cle, 0); return p; }
        p = (cle < p->e.cle) ? p->gauche : p->droit;
    }
    TRACE(EV_NOTFOUND, 0, 0, 0);
    return NULL;
}

int abr_compter(const ABR *a, int cle)
{
    Pile pile;
    int nb = 0;
    if (!a->racine) { TRACE(EV_COUNT, 0, 0, 0); return 0; }
    /* Les étudiants de moyenne `cle` forment un intervalle du parcours infixe.
     * Parcours ÉLAGUÉ : on ne descend à gauche que si la clé du nœud est >= cle,
     * à droite que si elle est <= cle. Nœuds visités : Θ(h + d), d = nb trouvé. */
    pile_init(&pile);
    pile_empiler(&pile, entree(a->racine, 0));
    while (pile.n > 0) {
        const Noeud *p = pile.t[--pile.n].noeud;
        CPT_CMP(); CPT_VIS();
        TRACE(EV_NODE_VISIT, p->e.id, p->e.cle, 0);
        if (cle == p->e.cle) { nb++; TRACE(EV_FOUND, p->e.id, p->e.cle, 0); }
        if (p->droit && cle >= p->e.cle) pile_empiler(&pile, entree(p->droit, 0));
        if (p->gauche && cle <= p->e.cle) pile_empiler(&pile, entree(p->gauche, 0));
    }
    pile_liberer(&pile);
    TRACE(EV_COUNT, nb, 0, 0);
    return nb;
}

int abr_supprimer(ABR *a, int cle, int id, Etudiant *supprime, int *cas)
{
    Noeud *pere = NULL, *p = a->racine;
    Etudiant cible;
    int c;

    cible.cle = cle;
    cible.id = id;
    while (p) {                                /* recherche du nœud et de son père */
        int r;
        CPT_CMP(); CPT_VIS();
        TRACE(EV_NODE_VISIT, p->e.id, p->e.cle, 0);
        if (id < 0) r = (cle == p->e.cle) ? 0 : (cle < p->e.cle ? -1 : 1);  /* moyenne seule */
        else        r = comparer_etudiants(&cible, &p->e);                 /* (moyenne, matricule) */
        if (r == 0) break;
        pere = p;
        p = (r < 0) ? p->gauche : p->droit;
    }
    if (!p) { TRACE(EV_NOTFOUND, 0, 0, 0); return 0; }
    TRACE(EV_FOUND, p->e.id, p->e.cle, 0);
    if (supprime) *supprime = p->e;

    if (p->gauche && p->droit) {
        /* CAS 3 : deux fils. On copie le successeur (min du sous-arbre droit)
         * dans le nœud, puis on retire le successeur (qui n'a pas de fils gauche). */
        Noeud *ps = p, *s = p->droit;
        c = 2;
        TRACE(EV_DEL_CASE, 2, p->e.id, 0);
        TRACE(EV_SUCC, s->e.id, s->e.cle, 0);
        CPT_VIS();
        while (s->gauche) {
            ps = s;
            s = s->gauche;
            CPT_VIS();
            TRACE(EV_SUCC, s->e.id, s->e.cle, 0);
        }
        TRACE(EV_NODE_REPLACE, p->e.id, s->e.id, 0);
        p->e = s->e;
        CPT_MOV();
        if (ps == p) ps->droit = s->droit;
        else ps->gauche = s->droit;
        TRACE(EV_NODE_REMOVE, s->e.id, 0, 0);
        FREE(s);
    } else {
        /* CAS 1 (feuille) ou CAS 2 (un seul fils) : le père adopte le fils éventuel. */
        Noeud *fils = p->gauche ? p->gauche : p->droit;
        c = fils ? 1 : 0;
        TRACE(EV_DEL_CASE, c, p->e.id, 0);
        if (!pere) a->racine = fils;
        else if (pere->gauche == p) pere->gauche = fils;
        else pere->droit = fils;
        TRACE(EV_NODE_REMOVE, p->e.id, 0, 0);
        FREE(p);
    }
    a->n--;
    if (cas) *cas = c;
    return 1;
}

int abr_trie(const ABR *a, Etudiant *sortie)
{
    Pile pile;
    const Noeud *p = a->racine;
    int i = 0;
    pile_init(&pile);
    while (p || pile.n > 0) {                  /* parcours infixe itératif */
        while (p) {
            if (!pile_empiler(&pile, entree(p, 0))) { pile_liberer(&pile); return -1; }
            p = p->gauche;
        }
        p = pile.t[--pile.n].noeud;
        CPT_VIS();
        TRACE(EV_NODE_VISIT, p->e.id, p->e.cle, 0);
        sortie[i++] = p->e;
        p = p->droit;
    }
    pile_liberer(&pile);
    return i;
}

int abr_topk(const ABR *a, int k, Etudiant *sortie)
{
    Pile pile;
    const Noeud *p = a->racine;
    int i = 0;
    pile_init(&pile);
    /* parcours infixe INVERSE (droit, nœud, gauche) arrêté après k étudiants */
    while (i < k && (p || pile.n > 0)) {
        while (p) {
            if (!pile_empiler(&pile, entree(p, 0))) { pile_liberer(&pile); return -1; }
            CPT_VIS();
            TRACE(EV_NODE_VISIT, p->e.id, p->e.cle, 0);
            p = p->droit;
        }
        p = pile.t[--pile.n].noeud;
        TRACE(EV_FOUND, p->e.id, p->e.cle, 0);
        sortie[i++] = p->e;
        p = p->gauche;
    }
    pile_liberer(&pile);
    return i;
}

/* Hauteur d'un sous-arbre par parcours en profondeur à pile explicite. */
static int hauteur_noeud(const Noeud *r, int *nb_feuilles, double *somme_prof)
{
    Pile pile;
    int h = 0;
    if (nb_feuilles) *nb_feuilles = 0;
    if (somme_prof) *somme_prof = 0.0;
    if (!r) return 0;
    pile_init(&pile);
    pile_empiler(&pile, entree(r, 1));
    while (pile.n > 0) {
        Entree e = pile.t[--pile.n];
        if (e.prof > h) h = e.prof;
        if (somme_prof) *somme_prof += e.prof;
        if (!e.noeud->gauche && !e.noeud->droit && nb_feuilles) (*nb_feuilles)++;
        if (e.noeud->gauche) pile_empiler(&pile, entree(e.noeud->gauche, e.prof + 1));
        if (e.noeud->droit)  pile_empiler(&pile, entree(e.noeud->droit, e.prof + 1));
    }
    pile_liberer(&pile);
    return h;
}

int abr_hauteur(const ABR *a)
{
    return hauteur_noeud(a->racine, NULL, NULL);
}

void abr_statistiques(const ABR *a, AbrStats *st)
{
    double somme = 0.0;
    st->hauteur = hauteur_noeud(a->racine, &st->nb_feuilles, &somme);
    st->hauteur_gauche = a->racine ? hauteur_noeud(a->racine->gauche, NULL, NULL) : 0;
    st->hauteur_droit  = a->racine ? hauteur_noeud(a->racine->droit, NULL, NULL) : 0;
    st->hauteur_min = a->n > 0 ? (int)ceil(log2((double)a->n + 1.0)) : 0;
    st->profondeur_moyenne = a->n > 0 ? somme / a->n : 0.0;
}

int abr_copier(ABR *dst, const ABR *src)
{
    Pile pile;
    Entree e;
    abr_init(dst);
    if (!src->racine) return 1;
    pile_init(&pile);
    e = entree(src->racine, 0);
    e.place = &dst->racine;
    pile_empiler(&pile, e);
    while (pile.n > 0) {
        Noeud *copie;
        e = pile.t[--pile.n];
        copie = (Noeud *)MALLOC(sizeof *copie);
        if (!copie) { pile_liberer(&pile); detruire_arbre(dst); return 0; }
        copie->e = e.noeud->e;
        copie->gauche = copie->droit = NULL;
        *e.place = copie;
        dst->n++;
        if (e.noeud->droit) {
            Entree f = entree(e.noeud->droit, 0);
            f.place = &copie->droit;
            pile_empiler(&pile, f);
        }
        if (e.noeud->gauche) {
            Entree f = entree(e.noeud->gauche, 0);
            f.place = &copie->gauche;
            pile_empiler(&pile, f);
        }
    }
    pile_liberer(&pile);
    return 1;
}

size_t abr_memoire(const ABR *a)
{
    return sizeof *a + (size_t)a->n * sizeof(Noeud);
}

int abr_exporter(const ABR *a, int *ids, int *cles, int *fg, int *fd, int max)
{
    Pile pile;
    int i = 0;
    if (!a->racine || max <= 0) return 0;
    pile_init(&pile);
    pile_empiler(&pile, entree(a->racine, 0));
    while (pile.n > 0 && i < max) {
        Entree e = pile.t[--pile.n];
        ids[i] = e.noeud->e.id;
        cles[i] = e.noeud->e.cle;
        fg[i] = fd[i] = -1;
        if (e.parent >= 0) {
            if (e.cote == 0) fg[e.parent] = i;
            else fd[e.parent] = i;
        }
        if (e.noeud->droit) {
            Entree f = entree(e.noeud->droit, 0);
            f.parent = i; f.cote = 1;
            pile_empiler(&pile, f);
        }
        if (e.noeud->gauche) {
            Entree f = entree(e.noeud->gauche, 0);
            f.parent = i; f.cote = 0;
            pile_empiler(&pile, f);
        }
        i++;
    }
    pile_liberer(&pile);
    return i;
}

/* Vérification de l'invariant : le parcours infixe doit être STRICTEMENT
 * croissant selon (moyenne, matricule) et contenir exactement n nœuds. */
int abr_verifier(const ABR *a)
{
    Pile pile;
    const Noeud *p = a->racine, *prec = NULL;
    int ok = 1, compte = 0;
    pile_init(&pile);
    while ((p || pile.n > 0) && ok) {
        while (p) { pile_empiler(&pile, entree(p, 0)); p = p->gauche; }
        p = pile.t[--pile.n].noeud;
        if (prec && comparer_etudiants(&prec->e, &p->e) >= 0) ok = 0;
        prec = p;
        compte++;
        p = p->droit;
    }
    pile_liberer(&pile);
    return ok && !pile.erreur && compte == a->n;
}

void abr_construire_sequentiel(ABR *a, const Etudiant *t, int n)
{
    int i;
    for (i = 0; i < n; i++) inserer_abr(a, &t[i]);
}

static void construire_equilibre_rec(ABR *a, const Etudiant *t, int g, int d)
{
    int m;
    if (g > d) return;
    m = g + (d - g) / 2;                  /* 1. trouver le milieu        */
    TRACE(EV_BUILD_RANGE, g, m, d);
    inserer_abr(a, &t[m]);                /* 2. insérer la moyenne du milieu */
    construire_equilibre_rec(a, t, g, m - 1);   /* 3. moitié gauche  */
    construire_equilibre_rec(a, t, m + 1, d);   /* 4. moitié droite  */
}

void abr_construire_equilibre(ABR *a, const Etudiant *tries, int n)
{
    construire_equilibre_rec(a, tries, 0, n - 1);
}
