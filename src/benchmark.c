/*
 * benchmark.c — Étude expérimentale (voir benchmark.h pour le protocole).
 */
#include "benchmark.h"
#include "annuaire.h"
#include "tris.h"
#include "tas.h"
#include "memoire.h"
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>

#ifndef OPTIONS_COMPILATION
#define OPTIONS_COMPILATION "non renseignees"
#endif

#define REP_RESULTATS  "resultats"
#define REP_SCRIPTS    "gnuplot"
#define REP_GRAPHES    "graphiques"

/* ======================================================================== */
/* 1. Chronométrage                                                         */
/* ======================================================================== */

static clock_t g_seuil;            /* en ticks d'horloge */
static clock_t g_plafond;
static volatile long long g_puits; /* empêche le compilateur de supprimer les appels */

/* Opération NON destructrice : répétée par lots (1, 2, 4, ...) dans une fenêtre
 * chronométrée jusqu'à ce que le temps cumulé atteigne le seuil.
 * Retourne le temps moyen d'un appel en secondes. */
static double chrono_repete(void (*op)(void *), void *ctx, long long *reps)
{
    clock_t cumul = 0, debut_mur = clock();
    long long n = 0;
    long lot = 1, i;
    for (;;) {
        clock_t t0 = clock(), t1;
        for (i = 0; i < lot; i++) op(ctx);
        t1 = clock();
        cumul += t1 - t0;
        n += lot;
        if (cumul >= g_seuil) break;
        if (clock() - debut_mur > g_plafond && cumul > 0) break;
        if (t1 - t0 < g_seuil / 4) lot *= 2;
    }
    *reps = n;
    return (double)cumul / CLOCKS_PER_SEC / (double)n;
}

/* Opération DESTRUCTRICE : prep() (recopie de la structure) et fin()
 * (destruction) sont exécutées HORS de la fenêtre chronométrée. */
static double chrono_prepare(void (*prep)(void *), void (*op)(void *), void (*fin)(void *),
                             void *ctx, long long *reps)
{
    clock_t cumul = 0, debut_mur = clock();
    long long n = 0;
    do {
        clock_t t0, t1;
        prep(ctx);
        t0 = clock();
        op(ctx);
        t1 = clock();
        fin(ctx);
        cumul += t1 - t0;
        n++;
    } while (cumul < g_seuil && (clock() - debut_mur <= g_plafond || cumul == 0));
    *reps = n;
    return (double)cumul / CLOCKS_PER_SEC / (double)n;
}

/* ======================================================================== */
/* 2. Stockage des résultats                                                */
/* ======================================================================== */

#define MAX_AGREG 6000
typedef struct {
    char   op[24];
    char   serie[40];
    int    n;
    double somme;      /* somme des valeurs sur les simulations */
    double reps;       /* somme des répétitions                  */
    int    nb;         /* nombre de simulations                  */
} Agreg;

static Agreg g_ag[MAX_AGREG];
static int   g_nag = 0;
static FILE *g_brut = NULL;
static FILE *g_journal = NULL;

static void enregistrer(const char *op, const char *serie, int n, int sim,
                        double valeur, long long reps)
{
    int i;
    if (g_brut)
        fprintf(g_brut, "%s,%s,%d,%d,%lld,%.6g\n", op, serie, n, sim, reps, valeur);
    for (i = 0; i < g_nag; i++)
        if (g_ag[i].n == n && !strcmp(g_ag[i].op, op) && !strcmp(g_ag[i].serie, serie)) break;
    if (i == g_nag) {
        if (g_nag == MAX_AGREG) return;
        g_nag++;
        strncpy(g_ag[i].op, op, sizeof g_ag[i].op - 1);
        g_ag[i].op[sizeof g_ag[i].op - 1] = '\0';
        strncpy(g_ag[i].serie, serie, sizeof g_ag[i].serie - 1);
        g_ag[i].serie[sizeof g_ag[i].serie - 1] = '\0';
        g_ag[i].n = n;
        g_ag[i].somme = g_ag[i].reps = 0;
        g_ag[i].nb = 0;
    }
    g_ag[i].somme += valeur;
    g_ag[i].reps += (double)reps;
    g_ag[i].nb++;
    if (g_journal) {
        fprintf(g_journal, "  n=%-6d %-15s %-28s %12.4f   (%lld rep.)\n", n, op, serie, valeur, reps);
        fflush(g_journal);
    }
}

/* Valeur moyenne d'une série ; retourne 0 si absente. */
static int valeur(const char *op, const char *serie, int n, double *v)
{
    int i;
    for (i = 0; i < g_nag; i++)
        if (g_ag[i].n == n && !strcmp(g_ag[i].op, op) && !strcmp(g_ag[i].serie, serie)) {
            *v = g_ag[i].somme / g_ag[i].nb;
            return 1;
        }
    return 0;
}

/* ======================================================================== */
/* 3. Contextes des opérations mesurées                                     */
/* ======================================================================== */

typedef struct {
    const Structure *maitre;   /* structure de référence (non modifiée)    */
    Structure  travail;        /* copie ou structure en construction       */
    int        type;
    int        equilibre;      /* construction : ABR équilibré (bonus 2)   */
    const Etudiant *jeu;
    int        n;
    const int *cles;           /* requêtes de recherche                    */
    int        nq;
    const Etudiant *cibles;    /* étudiants à supprimer                    */
    int        nb;
    Etudiant  *sortie;
    int        k, pivot;
} Ctx;

static void rien(void *v) { (void)v; }

static void op_construire(void *v)
{
    Ctx *c = (Ctx *)v;
    structure_init(&c->travail, c->type);
    if (c->equilibre) abr_construire_equilibre(&c->travail.u.s3, c->jeu, c->n);
    else structure_construire(&c->travail, c->jeu, c->n);
}
static void fin_travail(void *v) { structure_detruire(&((Ctx *)v)->travail); }

static void op_rechercher(void *v)
{
    Ctx *c = (Ctx *)v;
    int i;
    long long s = 0;
    for (i = 0; i < c->nq; i++) s += structure_rechercher(c->maitre, c->cles[i]);
    g_puits += s;
}

static void op_compter(void *v)
{
    Ctx *c = (Ctx *)v;
    int i;
    long long s = 0;
    for (i = 0; i < c->nq; i++) s += structure_compter(c->maitre, c->cles[i]);
    g_puits += s;
}

static void prep_copie(void *v)
{
    Ctx *c = (Ctx *)v;
    structure_copier(&c->travail, c->maitre);
}

static void op_supprimer(void *v)
{
    Ctx *c = (Ctx *)v;
    int i;
    long long s = 0;
    for (i = 0; i < c->nb; i++)
        s += structure_supprimer(&c->travail, c->cibles[i].cle, c->cibles[i].id, NULL, NULL);
    g_puits += s;
}

static void op_trie(void *v)
{
    Ctx *c = (Ctx *)v;
    g_puits += structure_trie(c->maitre, c->sortie, c->pivot);
    g_puits += c->sortie[0].cle;
}

static void op_topk(void *v)
{
    Ctx *c = (Ctx *)v;
    g_puits += structure_topk(c->maitre, c->k, c->sortie, c->pivot);
}

static void op_topk_tas(void *v)
{
    Ctx *c = (Ctx *)v;
    const S1Tableau *s = &c->maitre->u.s1t;
    g_puits += topk_tas(s->t, s->n, c->k, c->sortie);
}

/* ---- petites aides de mesure ------------------------------------------- */

static void mesurer_construction(const char *serie, int type, int equilibre,
                                 const Etudiant *jeu, int n, int sim)
{
    Ctx c;
    long long reps;
    double t;
    memset(&c, 0, sizeof c);
    c.type = type; c.equilibre = equilibre; c.jeu = jeu; c.n = n;
    t = chrono_prepare(rien, op_construire, fin_travail, &c, &reps);
    enregistrer("construction", serie, n, sim, t * 1e3, reps);         /* ms   */
    enregistrer("insertion", serie, n, sim, t * 1e6 / n, reps);        /* µs / insertion */
}

static void mesurer_recherche(const char *op, const char *serie, const Structure *s,
                              const int *cles, int nq, int n, int sim)
{
    Ctx c;
    long long reps;
    double t;
    memset(&c, 0, sizeof c);
    c.maitre = s; c.cles = cles; c.nq = nq;
    t = chrono_repete(!strcmp(op, "comptage") ? op_compter : op_rechercher, &c, &reps);
    enregistrer(op, serie, n, sim, t * 1e6 / nq, reps);                /* µs / requête */
}

static void mesurer_suppression(const char *serie, const Structure *s,
                                const Etudiant *cibles, int nb, int n, int sim)
{
    Ctx c;
    long long reps;
    double t;
    memset(&c, 0, sizeof c);
    c.maitre = s; c.cibles = cibles; c.nb = nb;
    t = chrono_prepare(prep_copie, op_supprimer, fin_travail, &c, &reps);
    enregistrer("suppression", serie, n, sim, t * 1e6 / nb, reps);     /* µs / suppression */
}

static void mesurer_trie(const char *serie, const Structure *s, int pivot,
                         Etudiant *sortie, int n, int sim)
{
    Ctx c;
    long long reps;
    double t;
    memset(&c, 0, sizeof c);
    c.maitre = s; c.sortie = sortie; c.pivot = pivot;
    t = chrono_repete(op_trie, &c, &reps);
    enregistrer("affichage_trie", serie, n, sim, t * 1e3, reps);       /* ms */
}

static void mesurer_topk(const char *op, const char *serie, const Structure *s, int tas,
                         int k, int pivot, Etudiant *sortie, int x, int sim)
{
    Ctx c;
    long long reps;
    double t;
    memset(&c, 0, sizeof c);
    c.maitre = s; c.sortie = sortie; c.k = k; c.pivot = pivot;
    t = chrono_repete(tas ? op_topk_tas : op_topk, &c, &reps);
    enregistrer(op, serie, x, sim, t * 1e6, reps);                     /* µs */
}

/* ======================================================================== */
/* 4. Déroulement d'une simulation pour une taille n                        */
/* ======================================================================== */

static void melanger(int *t, int n)
{
    int i;
    for (i = n - 1; i > 0; i--) {
        int j = (int)(((long)rand() * 32768L + rand()) % (i + 1)), x = t[i];
        t[i] = t[j];
        t[j] = x;
    }
}

static void simulation(const ConfigBench *cfg, int n, int sim, int nmax)
{
    const int nq = cfg->nb_requetes;
    const int B = n / 10 > 0 ? n / 10 : 1;          /* suppressions par répétition */
    Etudiant *alea, *crois, *decr, *sortie, *cib;
    int *req, *perm, i, cle_absente, present[CLE_MAX + 2];
    Structure s1t, s1l, s2, s3, s3c, s3d, s3e, s1c;
    AbrStats st;

    alea  = (Etudiant *)MALLOC((size_t)n * sizeof *alea);
    crois = (Etudiant *)MALLOC((size_t)n * sizeof *crois);
    decr  = (Etudiant *)MALLOC((size_t)n * sizeof *decr);
    sortie = (Etudiant *)MALLOC((size_t)(n + 1) * sizeof *sortie);
    cib   = (Etudiant *)MALLOC((size_t)B * sizeof *cib);
    req   = (int *)MALLOC((size_t)nq * sizeof *req);
    perm  = (int *)MALLOC((size_t)n * sizeof *perm);
    if (!alea || !crois || !decr || !sortie || !cib || !req || !perm) {
        fprintf(stderr, "Memoire insuffisante pour n = %d\n", n);
        goto fin;
    }

    /* ---- jeux de données (non chronométré) ---- */
    srand(cfg->graine + 7919u * (unsigned)sim + (unsigned)n);
    etudiant_raz_ids();
    generer_jeu(alea, n, GEN_ALEATOIRE);
    memcpy(crois, alea, (size_t)n * sizeof *alea);
    tri_rapide(crois, n, PIVOT_MEDIAN3);             /* mêmes étudiants, triés */
    for (i = 0; i < n; i++) decr[i] = crois[n - 1 - i];
    memset(present, 0, sizeof present);
    for (i = 0; i < n; i++) present[alea[i].cle] = 1;
    cle_absente = CLE_MAX + 1;                       /* moyenne absente > maximum */
    for (i = crois[n - 1].cle + 1; i <= CLE_MAX; i++) if (!present[i]) { cle_absente = i; break; }
    for (i = 0; i < n; i++) perm[i] = i;
    melanger(perm, n);

    if (g_journal) { fprintf(g_journal, "--- n = %d, simulation %d/%d ---\n", n, sim + 1, cfg->nb_simulations); fflush(g_journal); }

    /* ---- 1. AJOUT : construction par n insertions successives ---- */
    mesurer_construction("S1_tableau_alea", ST_S1_TABLEAU, 0, alea, n, sim);
    mesurer_construction("S1_tableau_croissant", ST_S1_TABLEAU, 0, crois, n, sim);
    mesurer_construction("S1_tableau_decroissant", ST_S1_TABLEAU, 0, decr, n, sim);
    mesurer_construction("S1_liste_alea", ST_S1_LISTE, 0, alea, n, sim);
    mesurer_construction("S1_liste_croissant", ST_S1_LISTE, 0, crois, n, sim);
    mesurer_construction("S1_liste_decroissant", ST_S1_LISTE, 0, decr, n, sim);
    mesurer_construction("S2_alea", ST_S2_TRIE, 0, alea, n, sim);
    mesurer_construction("S2_croissant", ST_S2_TRIE, 0, crois, n, sim);      /* meilleur cas */
    mesurer_construction("S2_decroissant", ST_S2_TRIE, 0, decr, n, sim);     /* pire cas     */
    mesurer_construction("S3_alea", ST_S3_ABR, 0, alea, n, sim);
    mesurer_construction("S3_croissant", ST_S3_ABR, 0, crois, n, sim);       /* dégénéré     */
    mesurer_construction("S3_decroissant", ST_S3_ABR, 0, decr, n, sim);      /* dégénéré     */
    mesurer_construction("S3_equilibre", ST_S3_ABR, 1, crois, n, sim);       /* bonus 2      */

    /* ---- structures de référence (non chronométré) ---- */
    structure_init(&s1t, ST_S1_TABLEAU); structure_construire(&s1t, alea, n);
    structure_init(&s1l, ST_S1_LISTE);   structure_construire(&s1l, alea, n);
    structure_init(&s2, ST_S2_TRIE);     structure_construire(&s2, alea, n);
    structure_init(&s3, ST_S3_ABR);      structure_construire(&s3, alea, n);
    structure_init(&s3c, ST_S3_ABR);     structure_construire(&s3c, crois, n);
    structure_init(&s3d, ST_S3_ABR);     structure_construire(&s3d, decr, n);
    structure_init(&s3e, ST_S3_ABR);     abr_construire_equilibre(&s3e.u.s3, crois, n);
    structure_init(&s1c, ST_S1_TABLEAU); structure_construire(&s1c, crois, n);

    /* hauteurs et mémoire */
    abr_statistiques(&s3.u.s3, &st);  enregistrer("hauteur", "S3_alea", n, sim, st.hauteur, 1);
    abr_statistiques(&s3c.u.s3, &st); enregistrer("hauteur", "S3_croissant", n, sim, st.hauteur, 1);
    abr_statistiques(&s3d.u.s3, &st); enregistrer("hauteur", "S3_decroissant", n, sim, st.hauteur, 1);
    abr_statistiques(&s3e.u.s3, &st); enregistrer("hauteur", "S3_equilibre", n, sim, st.hauteur, 1);
    enregistrer("hauteur", "log2_n", n, sim, log2((double)n), 1);
    enregistrer("memoire", "S1_tableau", n, sim, structure_memoire(&s1t) / 1024.0, 1);
    enregistrer("memoire", "S1_liste", n, sim, structure_memoire(&s1l) / 1024.0, 1);
    enregistrer("memoire", "S2", n, sim, structure_memoire(&s2) / 1024.0, 1);
    enregistrer("memoire", "S3", n, sim, structure_memoire(&s3) / 1024.0, 1);

    /* ---- 2. RECHERCHE (existence) ---- */
    for (i = 0; i < nq; i++) req[i] = alea[perm[i % n]].cle;         /* moyennes existantes */
    mesurer_recherche("recherche", "S1_tableau_moyen", &s1t, req, nq, n, sim);
    mesurer_recherche("recherche", "S1_liste_moyen", &s1l, req, nq, n, sim);
    mesurer_recherche("recherche", "S2_moyen", &s2, req, nq, n, sim);
    mesurer_recherche("recherche", "S3_moyen", &s3, req, nq, n, sim);
    mesurer_recherche("recherche", "S3_degenere_moyen", &s3c, req, nq, n, sim);
    mesurer_recherche("recherche", "S3_equilibre_moyen", &s3e, req, nq, n, sim);
    /* comptage des étudiants ayant ces moyennes */
    mesurer_recherche("comptage", "S1_tableau", &s1t, req, nq, n, sim);
    mesurer_recherche("comptage", "S1_liste", &s1l, req, nq, n, sim);
    mesurer_recherche("comptage", "S2", &s2, req, nq, n, sim);
    mesurer_recherche("comptage", "S3", &s3, req, nq, n, sim);
    mesurer_recherche("comptage", "S3_degenere", &s3c, req, nq, n, sim);
    mesurer_recherche("comptage", "S3_equilibre", &s3e, req, nq, n, sim);
    /* meilleurs cas : S1 = 1er arrivé, S2 = élément du milieu, S3 = racine */
    for (i = 0; i < nq; i++) req[i] = alea[0].cle;
    mesurer_recherche("recherche", "S1_tableau_meilleur", &s1t, req, nq, n, sim);
    mesurer_recherche("recherche", "S1_liste_meilleur", &s1l, req, nq, n, sim);
    for (i = 0; i < nq; i++) req[i] = s2.u.s2.t[(n - 1) / 2].cle;
    mesurer_recherche("recherche", "S2_meilleur", &s2, req, nq, n, sim);
    for (i = 0; i < nq; i++) req[i] = s3.u.s3.racine->e.cle;
    mesurer_recherche("recherche", "S3_meilleur", &s3, req, nq, n, sim);
    /* pires cas : moyenne absente (supérieure au maximum) */
    for (i = 0; i < nq; i++) req[i] = cle_absente;
    mesurer_recherche("recherche", "S1_tableau_pire", &s1t, req, nq, n, sim);
    mesurer_recherche("recherche", "S1_liste_pire", &s1l, req, nq, n, sim);
    mesurer_recherche("recherche", "S2_pire", &s2, req, nq, n, sim);
    mesurer_recherche("recherche", "S3_pire", &s3, req, nq, n, sim);
    mesurer_recherche("recherche", "S3_degenere_pire", &s3c, req, nq, n, sim);

    /* ---- 3. SUPPRESSION (B = n/10 étudiants par répétition, sur une copie) ---- */
    for (i = 0; i < B; i++) cib[i] = alea[perm[i]];                    /* au hasard */
    mesurer_suppression("S1_tableau_moyen", &s1t, cib, B, n, sim);
    mesurer_suppression("S1_liste_moyen", &s1l, cib, B, n, sim);
    mesurer_suppression("S2_moyen", &s2, cib, B, n, sim);
    mesurer_suppression("S3_moyen", &s3, cib, B, n, sim);
    mesurer_suppression("S3_equilibre_moyen", &s3e, cib, B, n, sim);
    for (i = 0; i < B; i++) cib[i] = alea[i];                          /* premiers arrivés */
    mesurer_suppression("S1_tableau_debut", &s1t, cib, B, n, sim);
    mesurer_suppression("S1_liste_debut", &s1l, cib, B, n, sim);
    for (i = 0; i < B; i++) cib[i] = alea[n - 1 - i];                  /* derniers arrivés */
    mesurer_suppression("S1_tableau_fin", &s1t, cib, B, n, sim);
    mesurer_suppression("S1_liste_fin", &s1l, cib, B, n, sim);
    for (i = 0; i < B; i++) cib[i] = crois[n - 1 - i];                 /* plus grandes moyennes */
    mesurer_suppression("S2_fin", &s2, cib, B, n, sim);
    mesurer_suppression("S3_degenere_fond", &s3c, cib, B, n, sim);
    for (i = 0; i < B; i++) cib[i] = crois[i];                         /* plus petites moyennes */
    mesurer_suppression("S2_debut", &s2, cib, B, n, sim);
    mesurer_suppression("S3_degenere_racine", &s3c, cib, B, n, sim);

    /* ---- 4. AFFICHAGE TRIÉ (production de la séquence triée, sans printf) ---- */
    mesurer_trie("S1_tableau_alea", &s1t, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_trie("S1_tableau_croissant", &s1c, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_trie("S1_tableau_pivot_dernier", &s1c, PIVOT_DERNIER, sortie, n, sim);
    mesurer_trie("S1_liste_alea", &s1l, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_trie("S2_alea", &s2, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_trie("S3_alea", &s3, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_trie("S3_degenere", &s3c, PIVOT_MEDIAN3, sortie, n, sim);

    /* ---- 5. TOP-K ---- */
    mesurer_topk("topk", "S1_tableau_alea", &s1t, 0, cfg->k, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_topk("topk", "S1_tableau_pivot_dernier", &s1c, 0, cfg->k, PIVOT_DERNIER, sortie, n, sim);
    mesurer_topk("topk", "S1_liste_alea", &s1l, 0, cfg->k, PIVOT_MEDIAN3, sortie, n, sim);
    mesurer_topk("topk", "S2_alea", &s2, 0, cfg->k, 0, sortie, n, sim);
    mesurer_topk("topk", "S3_alea", &s3, 0, cfg->k, 0, sortie, n, sim);
    mesurer_topk("topk", "S3_croissant", &s3c, 0, cfg->k, 0, sortie, n, sim);
    mesurer_topk("topk", "S3_decroissant", &s3d, 0, cfg->k, 0, sortie, n, sim);
    mesurer_topk("topk", "S3_equilibre", &s3e, 0, cfg->k, 0, sortie, n, sim);
    mesurer_topk("topk", "Tas_alea", &s1t, 1, cfg->k, 0, sortie, n, sim);   /* bonus 1 */

    /* top-k en fonction de k (taille maximale seulement) */
    if (n == nmax) {
        static const int ks[] = {1, 10, 100, 1000, 5000, 10000, 20000};
        int j;
        for (j = 0; j < (int)(sizeof ks / sizeof ks[0]); j++) {
            if (ks[j] > n) break;
            mesurer_topk("topk_k", "S1_tableau", &s1t, 0, ks[j], PIVOT_MEDIAN3, sortie, ks[j], sim);
            mesurer_topk("topk_k", "S2", &s2, 0, ks[j], 0, sortie, ks[j], sim);
            mesurer_topk("topk_k", "S3", &s3, 0, ks[j], 0, sortie, ks[j], sim);
            mesurer_topk("topk_k", "Tas", &s1t, 1, ks[j], 0, sortie, ks[j], sim);
        }
    }

    structure_detruire(&s1t); structure_detruire(&s1l); structure_detruire(&s2);
    structure_detruire(&s3);  structure_detruire(&s3c); structure_detruire(&s3d);
    structure_detruire(&s3e); structure_detruire(&s1c);
fin:
    FREE(alea); FREE(crois); FREE(decr); FREE(sortie); FREE(cib); FREE(req); FREE(perm);
}

/* ======================================================================== */
/* 5. Fichiers CSV                                                          */
/* ======================================================================== */

static const char *OPERATIONS[] = {
    "insertion", "construction", "recherche", "comptage", "suppression",
    "affichage_trie", "topk", "topk_k", "hauteur", "memoire"
};
#define NB_OPS ((int)(sizeof OPERATIONS / sizeof OPERATIONS[0]))

/* Liste ordonnée des séries d'une opération ; retourne leur nombre. */
static int series_de(const char *op, const char *series[], int max)
{
    int i, j, nb = 0;
    for (i = 0; i < g_nag && nb < max; i++) {
        if (strcmp(g_ag[i].op, op)) continue;
        for (j = 0; j < nb; j++) if (!strcmp(series[j], g_ag[i].serie)) break;
        if (j == nb) series[nb++] = g_ag[i].serie;
    }
    return nb;
}

/* Abscisses distinctes (triées) d'une opération. */
static int abscisses_de(const char *op, int xs[], int max)
{
    int i, j, nb = 0;
    for (i = 0; i < g_nag; i++) {
        if (strcmp(g_ag[i].op, op)) continue;
        for (j = 0; j < nb; j++) if (xs[j] == g_ag[i].n) break;
        if (j == nb && nb < max) xs[nb++] = g_ag[i].n;
    }
    for (i = 1; i < nb; i++) {                    /* tri par insertion */
        int x = xs[i];
        for (j = i - 1; j >= 0 && xs[j] > x; j--) xs[j + 1] = xs[j];
        xs[j + 1] = x;
    }
    return nb;
}

static void ecrire_csv_operations(void)
{
    int o;
    for (o = 0; o < NB_OPS; o++) {
        const char *series[64];
        int xs[64], ns, nx, i, j;
        char chemin[128];
        FILE *f;
        ns = series_de(OPERATIONS[o], series, 64);
        if (ns == 0) continue;
        nx = abscisses_de(OPERATIONS[o], xs, 64);
        snprintf(chemin, sizeof chemin, REP_RESULTATS "/%s.csv", OPERATIONS[o]);
        f = fopen(chemin, "w");
        if (!f) continue;
        fprintf(f, "%s", !strcmp(OPERATIONS[o], "topk_k") ? "k" : "N");
        for (j = 0; j < ns; j++) fprintf(f, ",%s", series[j]);
        fprintf(f, "\n");
        for (i = 0; i < nx; i++) {
            fprintf(f, "%d", xs[i]);
            for (j = 0; j < ns; j++) {
                double v;
                if (valeur(OPERATIONS[o], series[j], xs[i], &v)) fprintf(f, ",%.6g", v);
                else fprintf(f, ",NaN");
            }
            fprintf(f, "\n");
        }
        fclose(f);
    }
}

/* ======================================================================== */
/* 6. Scripts gnuplot (plusieurs courbes par graphe) et lancement system()  */
/* ======================================================================== */

typedef struct {
    const char *fichier;
    const char *titre;
    const char *op;
    const char *ylabel;
    int logx, logy;
    const char *series[8];
    const char *legendes[8];
    const char *theorie[8];   /* "1", "logn", "n", "nlogn", "n2" ou NULL */
} Graphe;

#define US "Temps moyen par operation (µs)"
#define MS "Temps total (ms)"

static const Graphe GRAPHES[] = {
    /* ---------------- S1 ---------------- */
    {"s1_insertion", "S1 - Ajout : temps moyen par insertion", "insertion", US, 0, 0,
     {"S1_tableau_alea", "S1_tableau_croissant", "S1_tableau_decroissant", "S1_liste_alea"},
     {"Tableau, ordre aleatoire", "Tableau, ordre croissant", "Tableau, ordre decroissant", "Liste chainee, ordre aleatoire"},
     {"1", NULL, NULL, "1"}},
    {"s1_recherche", "S1 - Recherche sequentielle (existence)", "recherche", US, 0, 0,
     {"S1_tableau_meilleur", "S1_tableau_moyen", "S1_tableau_pire", "S1_liste_meilleur", "S1_liste_moyen", "S1_liste_pire"},
     {"Tableau - meilleur cas (1er element)", "Tableau - cas moyen", "Tableau - pire cas (absente)",
      "Liste - meilleur cas", "Liste - cas moyen", "Liste - pire cas (absente)"},
     {"1", "n", "n", NULL, "n", "n"}},
    {"s1_comptage", "S1 - Nombre d'etudiants ayant une moyenne donnee", "comptage", US, 0, 0,
     {"S1_tableau", "S1_liste"}, {"Tableau", "Liste chainee"}, {"n", "n"}},
    {"s1_suppression", "S1 - Suppression : tableau (decalages) vs liste chainee", "suppression", US, 0, 0,
     {"S1_tableau_debut", "S1_tableau_moyen", "S1_tableau_fin", "S1_liste_debut", "S1_liste_moyen", "S1_liste_fin"},
     {"Tableau - 1er arrive (n-1 decalages)", "Tableau - au hasard", "Tableau - dernier arrive (n comparaisons)",
      "Liste - 1er arrive (meilleur cas)", "Liste - au hasard", "Liste - dernier arrive (pire cas)"},
     {"n", "n", "n", "1", "n", "n"}},
    {"s1_affichage_trie", "S1 - Affichage trie : copie + tri rapide", "affichage_trie", MS, 0, 0,
     {"S1_tableau_alea", "S1_tableau_croissant", "S1_liste_alea"},
     {"Tableau, donnees aleatoires", "Tableau, donnees deja triees (pivot median de 3)", "Liste chainee, donnees aleatoires"},
     {"nlogn", NULL, "nlogn"}},
    {"s1_topk", "S1 - Top-k (k = 10) : tri rapide puis k derniers", "topk", US, 0, 0,
     {"S1_tableau_alea", "S1_liste_alea"}, {"Tableau", "Liste chainee"}, {"nlogn", "nlogn"}},
    {"s1_tri_pire_cas", "S1 - Pire cas du tri rapide : pivot = dernier element sur donnees triees", "affichage_trie", MS, 0, 1,
     {"S1_tableau_alea", "S1_tableau_croissant", "S1_tableau_pivot_dernier"},
     {"Pivot median de 3, aleatoire", "Pivot median de 3, deja trie", "Pivot dernier, deja trie (pire cas)"},
     {"nlogn", "nlogn", "n2"}},
    /* ---------------- S2 ---------------- */
    {"s2_insertion", "S2 - Ajout avec maintien de l'ordre (principe du tri par insertion)", "insertion", US, 0, 0,
     {"S2_croissant", "S2_alea", "S2_decroissant"},
     {"Meilleur cas : arrivees croissantes (0 decalage)", "Cas moyen : arrivees aleatoires", "Pire cas : arrivees decroissantes"},
     {"1", "n", "n"}},
    {"s2_recherche", "S2 - Recherche dichotomique et comptage", "recherche", US, 0, 0,
     {"S2_meilleur", "S2_moyen", "S2_pire"},
     {"Meilleur cas (element du milieu)", "Cas moyen (moyenne existante)", "Pire cas (moyenne absente)"},
     {"1", "logn", "logn"}},
    {"s2_comptage", "S2 - Comptage par deux dichotomies (bornes inf. et sup.)", "comptage", US, 0, 0,
     {"S2"}, {"S2 tableau trie"}, {"logn"}},
    {"s2_suppression", "S2 - Suppression (dichotomie + decalages a gauche)", "suppression", US, 0, 0,
     {"S2_fin", "S2_moyen", "S2_debut"},
     {"Meilleur cas : plus grande moyenne (0 decalage)", "Cas moyen : au hasard", "Pire cas : plus petite moyenne (n decalages)"},
     {"logn", "n", "n"}},
    {"s2_affichage_trie", "S2 - Affichage trie : simple parcours", "affichage_trie", MS, 0, 0,
     {"S2_alea"}, {"S2"}, {"n"}},
    {"s2_topk", "S2 - Top-k (k = 10) : lecture directe des k derniers", "topk", US, 0, 0,
     {"S2_alea"}, {"S2"}, {"1"}},
    /* ---------------- S3 ---------------- */
    {"s3_insertion", "S3 - Ajout dans l'ABR (temps moyen par insertion)", "insertion", US, 0, 1,
     {"S3_alea", "S3_equilibre", "S3_croissant", "S3_decroissant"},
     {"Ordre aleatoire", "Construction equilibree (bonus 2)", "Ordre croissant (ABR degenere)", "Ordre decroissant (ABR degenere)"},
     {"logn", "logn", "n", "n"}},
    {"s3_recherche", "S3 - Recherche dans l'ABR", "recherche", US, 0, 1,
     {"S3_meilleur", "S3_moyen", "S3_pire", "S3_equilibre_moyen", "S3_degenere_moyen", "S3_degenere_pire"},
     {"Meilleur cas (racine)", "ABR aleatoire - moyenne existante", "ABR aleatoire - absente > max (branche droite)",
      "ABR equilibre - moyenne existante", "ABR degenere - moyenne existante", "ABR degenere - moyenne absente"},
     {"1", "logn", "logn", "logn", "n", "n"}},
    {"s3_comptage", "S3 - Comptage (parcours elague)", "comptage", US, 0, 1,
     {"S3", "S3_equilibre", "S3_degenere"}, {"ABR aleatoire", "ABR equilibre", "ABR degenere"},
     {"logn", "logn", "n"}},
    {"s3_suppression", "S3 - Suppression dans l'ABR", "suppression", US, 0, 1,
     {"S3_moyen", "S3_equilibre_moyen", "S3_degenere_racine", "S3_degenere_fond"},
     {"ABR aleatoire", "ABR equilibre", "ABR degenere - racine (meilleur cas)", "ABR degenere - feuille du fond (pire cas)"},
     {"logn", "logn", "1", "n"}},
    {"s3_affichage_trie", "S3 - Affichage trie : parcours infixe", "affichage_trie", MS, 0, 0,
     {"S3_alea", "S3_degenere"}, {"ABR aleatoire", "ABR degenere"}, {"n", "n"}},
    {"s3_topk", "S3 - Top-k (k = 10) : parcours infixe inverse arrete apres k", "topk", US, 0, 1,
     {"S3_decroissant", "S3_alea", "S3_equilibre", "S3_croissant"},
     {"Degenere a gauche : max a la racine (meilleur)", "ABR aleatoire", "ABR equilibre", "Degenere a droite : max au fond (pire)"},
     {"1", "logn", "logn", "n"}},
    {"s3_hauteur", "S3 - Hauteur de l'ABR selon l'ordre d'insertion", "hauteur", "Hauteur (niveaux)", 0, 1,
     {"S3_croissant", "S3_decroissant", "S3_alea", "S3_equilibre", "log2_n"},
     {"Insertion croissante", "Insertion decroissante", "Insertion aleatoire", "Construction equilibree (bonus 2)", "log2(n)"},
     {"n", NULL, "logn", NULL, NULL}},
    /* ---------------- Comparaisons S1 / S2 / S3 ---------------- */
    {"cmp_insertion", "Comparaison - Ajout (cas moyen, ordre aleatoire)", "insertion", US, 0, 1,
     {"S1_tableau_alea", "S1_liste_alea", "S2_alea", "S3_alea"},
     {"S1 tableau", "S1 liste chainee", "S2 tableau trie", "S3 ABR"}, {"1", "1", "n", "logn"}},
    {"cmp_recherche", "Comparaison - Recherche par moyenne (cas moyen)", "recherche", US, 0, 1,
     {"S1_tableau_moyen", "S1_liste_moyen", "S2_moyen", "S3_moyen"},
     {"S1 tableau", "S1 liste chainee", "S2 tableau trie", "S3 ABR"}, {"n", "n", "logn", "logn"}},
    {"cmp_comptage", "Comparaison - Nombre d'etudiants d'une moyenne", "comptage", US, 0, 1,
     {"S1_tableau", "S1_liste", "S2", "S3"},
     {"S1 tableau", "S1 liste chainee", "S2 tableau trie", "S3 ABR"}, {"n", "n", "logn", "logn"}},
    {"cmp_suppression", "Comparaison - Suppression (cas moyen)", "suppression", US, 0, 1,
     {"S1_tableau_moyen", "S1_liste_moyen", "S2_moyen", "S3_moyen"},
     {"S1 tableau", "S1 liste chainee", "S2 tableau trie", "S3 ABR"}, {"n", "n", "n", "logn"}},
    {"cmp_affichage_trie", "Comparaison - Affichage trie", "affichage_trie", MS, 0, 1,
     {"S1_tableau_alea", "S1_liste_alea", "S2_alea", "S3_alea"},
     {"S1 tableau", "S1 liste chainee", "S2 tableau trie", "S3 ABR"}, {"nlogn", "nlogn", "n", "n"}},
    {"cmp_topk", "Comparaison - Top-k (k = 10)", "topk", US, 0, 1,
     {"S1_tableau_alea", "S1_liste_alea", "S2_alea", "S3_alea"},
     {"S1 tableau (tri rapide)", "S1 liste chainee (tri rapide)", "S2 (lecture directe)", "S3 (infixe inverse)"},
     {"nlogn", "nlogn", "1", "logn"}},
    {"cmp_memoire", "Comparaison - Occupation memoire", "memoire", "Memoire (Ko)", 0, 0,
     {"S1_tableau", "S1_liste", "S2", "S3"},
     {"S1 tableau (capacite doublee)", "S1 liste chainee", "S2 tableau trie", "S3 ABR"}, {"n", "n", "n", "n"}},
    /* ---------------- Bonus ---------------- */
    {"bonus_tas_topk", "Bonus 1 - Top-k (k = 10) : tas max vs les trois structures", "topk", US, 0, 1,
     {"S1_tableau_alea", "Tas_alea", "S3_alea", "S2_alea"},
     {"S1 : tri rapide + k derniers", "Tas max : ConstruireTasMax + k extractions", "S3 : infixe inverse", "S2 : lecture directe"},
     {"nlogn", "n", "logn", "1"}},
    {"bonus_tas_topk_k", "Bonus 1 - Top-k en fonction de k (n maximal)", "topk_k", US, 1, 1,
     {"S1_tableau", "Tas", "S3", "S2"},
     {"S1 : tri rapide", "Tas max", "S3 : infixe inverse", "S2 : lecture directe"}, {NULL, NULL, NULL, NULL}},
    {"bonus_abr_construction", "Bonus 2 - Construction : ABR classique (moyennes croissantes) vs ABR equilibre", "construction", MS, 0, 1,
     {"S3_croissant", "S3_equilibre", "S3_alea"},
     {"ABR classique, insertions croissantes (pire cas)", "ABR equilibre (milieu d'abord)", "ABR classique, ordre aleatoire"},
     {"n2", "nlogn", "nlogn"}},
    {"bonus_abr_recherche", "Bonus 2 - Recherche : ABR degenere vs ABR equilibre", "recherche", US, 0, 1,
     {"S3_degenere_moyen", "S3_equilibre_moyen"},
     {"ABR classique degenere", "ABR equilibre"}, {"n", "logn"}},
};
#define NB_GRAPHES ((int)(sizeof GRAPHES / sizeof GRAPHES[0]))

static double f_theorie(const char *t, double n)
{
    if (!strcmp(t, "1"))     return 1.0;
    if (!strcmp(t, "logn"))  return log2(n);
    if (!strcmp(t, "n"))     return n;
    if (!strcmp(t, "nlogn")) return n * log2(n);
    return n * n;                                   /* "n2" */
}
static const char *expr_theorie(const char *t)
{
    if (!strcmp(t, "1"))     return "1";
    if (!strcmp(t, "logn"))  return "log(x)/log(2)";
    if (!strcmp(t, "n"))     return "x";
    if (!strcmp(t, "nlogn")) return "x*log(x)/log(2)";
    return "x**2";
}
static const char *nom_theorie(const char *t)
{
    if (!strcmp(t, "1"))     return "Θ(1)";
    if (!strcmp(t, "logn"))  return "Θ(log n)";
    if (!strcmp(t, "n"))     return "Θ(n)";
    if (!strcmp(t, "nlogn")) return "Θ(n log n)";
    return "Θ(n²)";
}

static const char *COULEURS[8] = {
    "#1f77b4", "#d62728", "#2ca02c", "#ff7f0e", "#9467bd", "#8c564b", "#e377c2", "#17becf"
};

/* Coefficient a minimisant  Σ (y - a f(n))²  sur les points de la série. */
static int ajuster(const char *op, const char *serie, const char *t, double *a)
{
    int xs[64], nx = abscisses_de(op, xs, 64), i, nb = 0;
    double num = 0, den = 0, v;
    for (i = 0; i < nx; i++)
        if (valeur(op, serie, xs[i], &v) && xs[i] > 1) {
            double f = f_theorie(t, xs[i]);
            num += v * f;
            den += f * f;
            nb++;
        }
    if (nb == 0 || den <= 0) return 0;
    *a = num / den;
    return 1;
}

static int colonne_de(const char *op, const char *serie)
{
    const char *series[64];
    int ns = series_de(op, series, 64), j;
    for (j = 0; j < ns; j++) if (!strcmp(series[j], serie)) return j + 2;
    return -1;
}

static void ecrire_script(const Graphe *g, FILE *tous)
{
    char chemin[128];
    FILE *f;
    int i, premier = 1;
    snprintf(chemin, sizeof chemin, REP_SCRIPTS "/%s.gp", g->fichier);
    f = fopen(chemin, "w");
    if (!f) return;
    fprintf(f, "# Genere automatiquement par benchmark.c — %s\n", g->titre);
    fprintf(f, "# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),\n");
    fprintf(f, "# a ajuste par moindres carres sur les mesures de la meme serie.\n");
    fprintf(f, "set encoding utf8\n");
    fprintf(f, "set terminal pngcairo size 1100,680 enhanced font 'Arial,11'\n");
    fprintf(f, "set output '" REP_GRAPHES "/%s.png'\n", g->fichier);
    fprintf(f, "set datafile separator ','\nset datafile columnheaders\n");
    fprintf(f, "set title \"%s\" font 'Arial,14'\n", g->titre);
    fprintf(f, "set xlabel \"%s\"\n", !strcmp(g->op, "topk_k") ? "k (nombre de meilleurs etudiants)" : "Taille de la base n");
    fprintf(f, "set ylabel \"%s\"\n", g->ylabel);
    fprintf(f, "set grid lc rgb '#dddddd'\nset key left top box opaque font 'Arial,9'\n");
    if (g->logx) fprintf(f, "set logscale x\n");
    if (g->logy) fprintf(f, "set logscale y\n");
    for (i = 0; i < 8 && g->series[i]; i++) {
        double a;
        if (g->theorie[i] && ajuster(g->op, g->series[i], g->theorie[i], &a))
            fprintf(f, "f%d(x) = %.10g * %s\n", i, a, expr_theorie(g->theorie[i]));
    }
    fprintf(f, "plot ");
    for (i = 0; i < 8 && g->series[i]; i++) {
        int col = colonne_de(g->op, g->series[i]);
        double a;
        if (col < 0) continue;
        fprintf(f, "%s'" REP_RESULTATS "/%s.csv' using 1:%d with linespoints lw 2 pt 7 ps 0.8 lc rgb '%s' title \"%s\"",
                premier ? "" : ", \\\n     ", g->op, col, COULEURS[i], g->legendes[i]);
        premier = 0;
        if (g->theorie[i] && ajuster(g->op, g->series[i], g->theorie[i], &a))
            fprintf(f, ", \\\n     f%d(x) with lines dt 2 lw 1.5 lc rgb '%s' title \"  theorie %s\"",
                    i, COULEURS[i], nom_theorie(g->theorie[i]));
    }
    fprintf(f, "\nunset output\n");
    fclose(f);
    if (tous) fprintf(tous, "reset\nload '" REP_SCRIPTS "/%s.gp'\n", g->fichier);
}

static const char *executable_gnuplot(void)
{
    static char chemin[512] = "";
    const char *env = getenv("GNUPLOT");
    FILE *f;
    if (chemin[0]) return chemin;
    if (env && env[0]) { strncpy(chemin, env, sizeof chemin - 1); return chemin; }
#ifdef _WIN32
    if (system("gnuplot --version > NUL 2>&1") == 0) { strcpy(chemin, "gnuplot"); return chemin; }
    {   /* emplacements usuels de MSYS2 et de l'installateur officiel */
        static const char *candidats[] = {
            "C:\\msys64\\clang64\\bin\\gnuplot.exe",
            "C:\\msys64\\ucrt64\\bin\\gnuplot.exe",
            "C:\\msys64\\mingw64\\bin\\gnuplot.exe",
            "C:\\Program Files\\gnuplot\\bin\\gnuplot.exe"
        };
        int i;
        for (i = 0; i < 4; i++) {
            char cmd[300];
            f = fopen(candidats[i], "rb");
            if (!f) continue;
            fclose(f);
            snprintf(cmd, sizeof cmd, "\"\"%s\" --version > NUL 2>&1\"", candidats[i]);
            if (system(cmd) == 0) {             /* l'exécutable démarre vraiment */
                snprintf(chemin, sizeof chemin, "\"%s\"", candidats[i]);
                return chemin;
            }
        }
    }
#else
    (void)f;
    if (system("gnuplot --version > /dev/null 2>&1") == 0) { strcpy(chemin, "gnuplot"); return chemin; }
#endif
    return NULL;
}

int bench_lancer_gnuplot(FILE *journal)
{
    char cmd[700];
    const char *gp = executable_gnuplot();
    int r;
    if (!gp) {
        if (journal) fprintf(journal, "gnuplot introuvable : definir la variable GNUPLOT ou l'ajouter au PATH.\n"
                                      "Les scripts sont dans " REP_SCRIPTS "/ (gnuplot " REP_SCRIPTS "/tous.gp).\n");
        return 1;
    }
#ifdef _WIN32
    snprintf(cmd, sizeof cmd, "\"%s " REP_SCRIPTS "/tous.gp 2> " REP_SCRIPTS "/gnuplot.log\"", gp);   /* guillemets pour cmd.exe ; messages dans gnuplot.log */
#else
    snprintf(cmd, sizeof cmd, "%s " REP_SCRIPTS "/tous.gp 2> " REP_SCRIPTS "/gnuplot.log", gp);
#endif
    if (journal) { fprintf(journal, "Lancement : system(\"%s\")\n", cmd); fflush(journal); }
    r = system(cmd);                                 /* gnuplot lancé par system() */
    if (journal) fprintf(journal, r == 0 ? "Graphiques PNG ecrits dans " REP_GRAPHES "/\n"
                                         : "gnuplot a signale une erreur (code %d)\n", r);
    return r;
}

static void ecrire_protocole(const ConfigBench *c, double duree)
{
    FILE *f = fopen(REP_RESULTATS "/protocole.txt", "w");
    int i;
    time_t maintenant = time(NULL);
    if (!f) return;
    fprintf(f, "PROTOCOLE EXPERIMENTAL — Mini-projet A\n");
    fprintf(f, "Date                    : %s", ctime(&maintenant));
    fprintf(f, "Compilateur             : gcc %s\n", __VERSION__);
    fprintf(f, "Options de compilation  : %s\n", OPTIONS_COMPILATION);
    fprintf(f, "Horloge                 : clock(), CLOCKS_PER_SEC = %ld\n", (long)CLOCKS_PER_SEC);
    fprintf(f, "Tailles n               :");
    for (i = 0; i < c->nb_tailles; i++) fprintf(f, " %d", c->tailles[i]);
    fprintf(f, "\nSimulations par taille  : %d (jeux aleatoires differents, resultats moyennes)\n", c->nb_simulations);
    fprintf(f, "Seuil par mesure        : %.0f ms de temps chronometre cumule (repetitions)\n", c->seuil_ms);
    fprintf(f, "Plafond par mesure      : %.1f s\n", c->plafond_s);
    fprintf(f, "k (top-k)               : %d\n", c->k);
    fprintf(f, "Requetes par lot        : %d\n", c->nb_requetes);
    fprintf(f, "Suppressions par rep.   : n/10 (sur une copie de la structure, copie non chronometree)\n");
    fprintf(f, "Graine srand()          : %u\n", c->graine);
    fprintf(f, "Duree totale            : %.1f s\n", duree);
    fprintf(f, "\nUnites : insertion/recherche/comptage/suppression/topk en microsecondes par operation ;\n");
    fprintf(f, "construction et affichage_trie en millisecondes ; hauteur en niveaux ; memoire en Ko.\n");
    fprintf(f, "insertion = temps de construction par n insertions successives / n.\n");
    fprintf(f, "affichage_trie = production de la sequence triee dans un tableau (sans printf, pour ne pas\n");
    fprintf(f, "mesurer la console).\n");
    fclose(f);
}

/* ======================================================================== */
/* 7. Point d'entrée                                                        */
/* ======================================================================== */

void bench_config_defaut(ConfigBench *c)
{
    static const int t[] = {1000, 2000, 5000, 10000, 15000, 20000};
    int i;
    memset(c, 0, sizeof *c);
    c->nb_tailles = (int)(sizeof t / sizeof t[0]);
    for (i = 0; i < c->nb_tailles; i++) c->tailles[i] = t[i];
    c->nb_simulations = 3;
    c->seuil_ms = 100.0;
    c->plafond_s = 3.0;
    c->k = 10;
    c->nb_requetes = 200;
    c->graine = 2026;
    c->gnuplot = 1;
}

void bench_config_rapide(ConfigBench *c)
{
    static const int t[] = {500, 1000, 2000, 4000, 6000, 8000};
    int i;
    bench_config_defaut(c);
    c->nb_tailles = (int)(sizeof t / sizeof t[0]);
    for (i = 0; i < c->nb_tailles; i++) c->tailles[i] = t[i];
    c->nb_simulations = 1;
    c->seuil_ms = 20.0;
    c->plafond_s = 1.0;
    c->nb_requetes = 100;
}

int bench_executer(const ConfigBench *c, FILE *journal)
{
    int i, s, total, fait = 0, nmax = 0;
    clock_t debut = clock();
    FILE *tous;

    g_journal = journal;
    g_nag = 0;
    g_seuil = (clock_t)(c->seuil_ms * CLOCKS_PER_SEC / 1000.0);
    if (g_seuil < 1) g_seuil = 1;
    g_plafond = (clock_t)(c->plafond_s * CLOCKS_PER_SEC);
    for (i = 0; i < c->nb_tailles; i++) if (c->tailles[i] > nmax) nmax = c->tailles[i];

    g_brut = fopen(REP_RESULTATS "/mesures_brutes.csv", "w");
    if (!g_brut) {
        if (journal) fprintf(journal, "Impossible d'ecrire dans " REP_RESULTATS "/ (lancer depuis la racine du projet)\n");
        return 1;
    }
    fprintf(g_brut, "operation,serie,N,simulation,repetitions,valeur\n");

    total = c->nb_tailles * c->nb_simulations;
    for (i = 0; i < c->nb_tailles; i++)
        for (s = 0; s < c->nb_simulations; s++) {
            simulation(c, c->tailles[i], s, nmax);
            fait++;
            if (journal) { fprintf(journal, "PROGRESSION %d/%d\n", fait, total); fflush(journal); }
        }
    fclose(g_brut);
    g_brut = NULL;

    ecrire_csv_operations();
    tous = fopen(REP_SCRIPTS "/tous.gp", "w");
    for (i = 0; i < NB_GRAPHES; i++) ecrire_script(&GRAPHES[i], tous);
    if (tous) fclose(tous);
    ecrire_protocole(c, (double)(clock() - debut) / CLOCKS_PER_SEC);
    if (journal) fprintf(journal, "CSV ecrits dans " REP_RESULTATS "/, scripts dans " REP_SCRIPTS "/\n");
    if (c->gnuplot) bench_lancer_gnuplot(journal);
    if (journal) { fprintf(journal, "TERMINE en %.1f s\n", (double)(clock() - debut) / CLOCKS_PER_SEC); fflush(journal); }
    g_journal = NULL;
    return 0;
}
