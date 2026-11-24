/*
 * api.c — Bibliothèque partagée pour l'interface graphique (voir api.h).
 */
#include "api.h"
#include "annuaire.h"
#include "tris.h"
#include "tas.h"
#include "memoire.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>

static Annuaire g_a;
static int g_init = 0;
static ABR g_anim;               /* petit ABR de démonstration (visualiseur) */
static int g_anim_id = 1;        /* matricules des nœuds de démonstration    */

/* Début / fin d'une opération : remise à zéro des compteurs et de la trace. */
static void debut(int trace) { compteurs_raz(); trace_vider(); trace_activer(trace); }
static void fin(void)        { trace_activer(0); }

API int api_version(void)         { return 1; }
API int api_taille_etudiant(void) { return (int)sizeof(Etudiant); }

API void api_init(void)
{
    if (g_init) annuaire_vider(&g_a);
    else annuaire_init(&g_a);
    abr_init(&g_anim);
    g_init = 1;
}

API void api_liberer(void)
{
    if (!g_init) return;
    annuaire_vider(&g_a);
    detruire_arbre(&g_anim);
    trace_liberer();
    g_init = 0;
}

API int api_taille(void) { return annuaire_taille(&g_a); }

API int api_generer(int n, int mode, unsigned graine)
{
    int ok;
    srand(graine);
    etudiant_raz_ids();
    debut(0);
    ok = annuaire_generer(&g_a, n, mode);
    fin();
    return ok;
}

API int api_ajouter(const char *nom, const char *prenom, int age, char sexe,
                    const float *notes, int trace_structure, int *id)
{
    Etudiant e;
    Compteurs c = {0, 0, 0};
    int err = etudiant_remplir(&e, nom, prenom, age, sexe, notes), s, ok = 1;
    if (err != ETU_OK) return err;
    e.id = etudiant_nouvel_id();
    debut(0);
    /* insertion dans les 4 structures ; seule la structure observée est tracée
     * et ses compteurs sont conservés */
    for (s = 0; s < NB_STRUCTURES; s++) {
        if (s == trace_structure) { compteurs_raz(); trace_activer(1); }
        ok &= structure_ajouter(&g_a.s[s], &e);
        if (s == trace_structure) { trace_activer(0); c = compteurs_lire(); }
    }
    g_cpt = c;
    fin();
    if (id) *id = e.id;
    return ok ? ETU_OK : -1;
}

API const char *api_message_erreur(int code) { return etudiant_message_erreur(code); }

API int api_supprimer(int cle, int id, int trace_structure, Etudiant *supprime, int *cas)
{
    int s, ok = 1;
    Compteurs c = {0, 0, 0};
    if (cas) *cas = -1;
    if (id < 0) {                    /* le premier arrivé ayant cette moyenne */
        const S1Tableau *s1 = &g_a.s[ST_S1_TABLEAU].u.s1t;
        int pos = s1t_rechercher(s1, cle);
        if (pos < 0) return 0;
        id = s1->t[pos].id;
    }
    debut(0);
    for (s = 0; s < NB_STRUCTURES; s++) {
        int cs = -1;
        if (s == trace_structure) { compteurs_raz(); trace_activer(1); }
        ok &= structure_supprimer(&g_a.s[s], cle, id, s == 0 ? supprime : NULL, &cs);
        if (s == trace_structure) { trace_activer(0); c = compteurs_lire(); }
        if (s == ST_S3_ABR && cas) *cas = cs;
    }
    g_cpt = c;
    fin();
    return ok;
}

API int api_rechercher(int s, int cle, int trace)
{
    int r;
    if (s < 0 || s >= NB_STRUCTURES) return 0;
    debut(trace);
    r = structure_rechercher(&g_a.s[s], cle);
    fin();
    return r;
}

API int api_compter(int s, int cle, int trace)
{
    int r;
    if (s < 0 || s >= NB_STRUCTURES) return 0;
    debut(trace);
    r = structure_compter(&g_a.s[s], cle);
    fin();
    return r;
}

API int api_trie(int s, Etudiant *sortie, int trace)
{
    int r;
    if (s < 0 || s >= NB_STRUCTURES) return 0;
    debut(trace);
    r = structure_trie(&g_a.s[s], sortie, g_mode_pivot);
    fin();
    return r;
}

API int api_topk(int methode, int k, Etudiant *sortie, int trace)
{
    int r;
    debut(trace);
    r = annuaire_topk(&g_a, methode, k, sortie);
    fin();
    return r;
}

API int api_contenu(int s, Etudiant *sortie)
{
    if (s < 0 || s >= NB_STRUCTURES) return 0;
    return structure_contenu(&g_a.s[s], sortie);
}

API int api_trouver(int id, Etudiant *e) { return annuaire_trouver_id(&g_a, id, e); }

API double api_memoire(int s)
{
    if (s < 0 || s >= NB_STRUCTURES) return 0;
    return (double)structure_memoire(&g_a.s[s]);
}

API void api_definir_pivot(int mode) { g_mode_pivot = mode ? PIVOT_DERNIER : PIVOT_MEDIAN3; }

API void api_abr_stats(int *hauteur, int *hg, int *hd, int *feuilles, int *hmin, double *prof)
{
    AbrStats st;
    abr_statistiques(&g_a.s[ST_S3_ABR].u.s3, &st);
    *hauteur = st.hauteur; *hg = st.hauteur_gauche; *hd = st.hauteur_droit;
    *feuilles = st.nb_feuilles; *hmin = st.hauteur_min; *prof = st.profondeur_moyenne;
}

API int api_abr_exporter(int *ids, int *cles, int *fg, int *fd, int max)
{
    return abr_exporter(&g_a.s[ST_S3_ABR].u.s3, ids, cles, fg, fd, max);
}

API double api_mesurer(int op, int s, int param, long long *reps)
{
    clock_t t0 = clock(), t1;
    long long n = 0, puits = 0;
    int taille = annuaire_taille(&g_a);
    Etudiant *buf = (Etudiant *)MALLOC((size_t)(taille + 1) * sizeof *buf);
    if (!buf) return -1;
    trace_activer(0);
    do {
        switch (op) {
        case 0: puits += structure_rechercher(&g_a.s[s], param); break;
        case 1: puits += structure_compter(&g_a.s[s], param); break;
        case 2: puits += structure_trie(&g_a.s[s], buf, g_mode_pivot); break;
        default: puits += annuaire_topk(&g_a, s, param, buf); break;
        }
        n++;
        t1 = clock();
    } while (t1 - t0 < CLOCKS_PER_SEC / 20);
    FREE(buf);
    if (reps) *reps = n;
    (void)puits;
    return (double)(t1 - t0) * 1e6 / CLOCKS_PER_SEC / (double)n;
}

API void api_compteurs(long long *cmp, long long *mov, long long *vis)
{
    Compteurs c = compteurs_lire();
    *cmp = c.comparaisons; *mov = c.mouvements; *vis = c.visites;
}

API int api_trace_taille(void)   { return trace_taille(); }
API int api_trace_tronquee(void) { return trace_tronquee(); }

API int api_trace_lire(EvenementTrace *buf, int max)
{
    int n = trace_taille();
    if (n > max) n = max;
    if (n > 0) memcpy(buf, trace_donnees(), (size_t)n * sizeof *buf);
    return n;
}

/* ------------------------------------------------------------------------- */
/* Animations : données de démonstration, mais VRAIES fonctions du projet.    */
/* ------------------------------------------------------------------------- */

static Etudiant *tableau_demo(const int *cles, int n)
{
    Etudiant *t = (Etudiant *)MALLOC((size_t)(n + 1) * sizeof *t);
    int i;
    if (!t) return NULL;
    memset(t, 0, (size_t)(n + 1) * sizeof *t);
    for (i = 0; i < n; i++) {
        t[i].id = i;                       /* départage des égalités = indice initial */
        t[i].cle = cles[i];
        t[i].moyenne = (float)(cles[i] / 100.0);
    }
    return t;
}

API int api_anim_tri_rapide(const int *cles, int n, int pivot, int *resultat)
{
    Etudiant *t = tableau_demo(cles, n);
    int i;
    if (!t) return -1;
    debut(1);
    tri_rapide(t, n, pivot ? PIVOT_DERNIER : PIVOT_MEDIAN3);     /* tri de S1 */
    fin();
    for (i = 0; i < n; i++) resultat[i] = t[i].cle;
    FREE(t);
    return trace_taille();
}

API int api_anim_tri_insertion(const int *cles, int n, int *resultat)
{
    Etudiant *t = tableau_demo(cles, n);
    int i;
    if (!t) return -1;
    debut(1);
    tri_insertion(t, n);                   /* même inserer_dans_trie() que S2 */
    fin();
    for (i = 0; i < n; i++) resultat[i] = t[i].cle;
    FREE(t);
    return trace_taille();
}

API int api_anim_dichotomie(const int *cles, int n, int cle, int mode, int *trie)
{
    Etudiant *t = tableau_demo(cles, n);
    S2Tableau s;
    int i, r;
    if (!t) return -1;
    s2_init(&s);
    for (i = 0; i < n; i++) s2_ajouter(&s, &t[i]);       /* non tracé */
    for (i = 0; i < n; i++) trie[i] = s.t[i].cle;
    debut(1);
    r = mode ? s2_compter(&s, cle) : s2_rechercher(&s, cle);
    fin();
    s2_detruire(&s);
    FREE(t);
    return r;
}

API int api_anim_tas(const int *cles, int n, int k, int *extraits)
{
    Etudiant *t = tableau_demo(cles, n), *sortie;
    int i, r;
    if (!t) return -1;
    sortie = (Etudiant *)MALLOC((size_t)(k > 0 ? k : 1) * sizeof *sortie);
    if (!sortie) { FREE(t); return -1; }
    debut(1);
    r = topk_tas(t, n, k, sortie);         /* ConstruireTasMax + k extractions */
    fin();
    for (i = 0; i < r; i++) extraits[i] = sortie[i].cle;
    FREE(sortie);
    FREE(t);
    return r;
}

API void api_anim_abr_vider(void)
{
    detruire_arbre(&g_anim);
    g_anim_id = 1;
}

static Etudiant noeud_demo(int cle)
{
    Etudiant e;
    memset(&e, 0, sizeof e);
    e.id = g_anim_id++;
    e.cle = cle;
    e.moyenne = (float)(cle / 100.0);
    return e;
}

API int api_anim_abr_inserer(int cle)
{
    Etudiant e = noeud_demo(cle);
    debut(1);
    inserer_abr(&g_anim, &e);
    fin();
    return e.id;
}

API int api_anim_abr_sequence(const int *cles, int n, int equilibre)
{
    Etudiant *t = (Etudiant *)MALLOC((size_t)(n + 1) * sizeof *t);
    int i;
    if (!t) return -1;
    for (i = 0; i < n; i++) t[i] = noeud_demo(cles[i]);
    detruire_arbre(&g_anim);
    if (equilibre) tri_rapide(t, n, PIVOT_MEDIAN3);      /* moyennes triées */
    debut(1);
    if (equilibre) abr_construire_equilibre(&g_anim, t, n);
    else abr_construire_sequentiel(&g_anim, t, n);
    fin();
    FREE(t);
    return trace_taille();
}

API int api_anim_abr_rechercher(int cle)
{
    const Noeud *p;
    debut(1);
    p = abr_rechercher(&g_anim, cle);
    fin();
    return p ? p->e.id : -1;
}

API int api_anim_abr_compter(int cle)
{
    int r;
    debut(1);
    r = abr_compter(&g_anim, cle);
    fin();
    return r;
}

API int api_anim_abr_supprimer(int cle, int *cas)
{
    int r;
    debut(1);
    r = abr_supprimer(&g_anim, cle, -1, NULL, cas);
    fin();
    return r;
}

API int api_anim_abr_topk(int k, int *cles_sortie)
{
    Etudiant *sortie = (Etudiant *)MALLOC((size_t)(k > 0 ? k : 1) * sizeof *sortie);
    int i, r;
    if (!sortie) return -1;
    debut(1);
    r = abr_topk(&g_anim, k, sortie);
    fin();
    for (i = 0; i < r; i++) cles_sortie[i] = sortie[i].cle;
    FREE(sortie);
    return r;
}

API int api_anim_abr_exporter(int *ids, int *cles, int *fg, int *fd, int max)
{
    return abr_exporter(&g_anim, ids, cles, fg, fd, max);
}

API int api_anim_abr_taille(void) { return g_anim.n; }

API int api_anim_abr_hauteur(void) { return abr_hauteur(&g_anim); }

/* Temps moyen (ms) de construction : répétée jusqu'à 100 ms cumulées,
 * la destruction de l'arbre n'est pas chronométrée. */
static double chrono_construction(const Etudiant *t, int n, int equilibre, int *hauteur)
{
    clock_t cumul = 0;
    long rep = 0;
    ABR a;
    do {
        clock_t t0, t1;
        abr_init(&a);
        t0 = clock();
        if (equilibre) abr_construire_equilibre(&a, t, n);
        else abr_construire_sequentiel(&a, t, n);
        t1 = clock();
        cumul += t1 - t0;
        rep++;
        if (cumul >= CLOCKS_PER_SEC / 10) *hauteur = abr_hauteur(&a);
        detruire_arbre(&a);
    } while (cumul < CLOCKS_PER_SEC / 10);
    return (double)cumul * 1e3 / CLOCKS_PER_SEC / rep;
}

API int api_bench_abr(int n, unsigned graine, double *t_classique, double *t_equilibre,
                      int *h_classique, int *h_equilibre)
{
    Etudiant *t;
    if (n < 1) return 0;
    t = (Etudiant *)MALLOC((size_t)n * sizeof *t);
    if (!t) return 0;
    srand(graine);
    generer_jeu(t, n, GEN_CROISSANT);          /* moyennes triées (non chronométré) */
    trace_activer(0);
    *t_classique = chrono_construction(t, n, 0, h_classique);
    *t_equilibre = chrono_construction(t, n, 1, h_equilibre);
    FREE(t);
    return 1;
}
