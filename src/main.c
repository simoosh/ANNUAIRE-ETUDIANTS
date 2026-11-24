/*
 * main.c — Programme en ligne de commande : menu qui résume l'ensemble du travail.
 *
 * Utilisation :
 *   annuaire                      menu interactif
 *   annuaire --bench [options]    étude expérimentale non interactive
 *       --rapide                  tailles réduites (démonstration)
 *       --tailles 1000,2000,...   tailles n
 *       --sims S                  simulations par taille
 *       --seuil MS                temps cumulé minimal par mesure
 *       --sans-gnuplot            n'appelle pas gnuplot
 *   annuaire --gnuplot            relance gnuplot sur les scripts existants
 *   --dossier CHEMIN              répertoire du projet (resultats/, graphiques/, ...)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "annuaire.h"
#include "tris.h"
#include "tas.h"
#include "benchmark.h"
#include "memoire.h"

#ifdef _WIN32
#include <windows.h>
#include <direct.h>
#define changer_dossier _chdir
#else
#include <unistd.h>
#define changer_dossier chdir
#endif

static Annuaire g_annuaire;
static int g_active = ST_S2_TRIE;       /* structure active ; -1 = toutes */

/* ------------------------------------------------------------------------- */
/* Saisie sécurisée                                                           */
/* ------------------------------------------------------------------------- */

static int lire_ligne(const char *invite, char *buf, int taille)
{
    size_t n;
    printf("%s", invite);
    fflush(stdout);
    if (!fgets(buf, taille, stdin)) return 0;
    n = strlen(buf);
    if (n > 0 && buf[n - 1] == '\n') buf[--n] = '\0';
    else { int c; while ((c = getchar()) != '\n' && c != EOF) {} }   /* ligne trop longue */
    if (n > 0 && buf[n - 1] == '\r') buf[--n] = '\0';
    return 1;
}

static int lire_entier(const char *invite, int min, int max, int *v)
{
    char buf[64], *fin;
    long x;
    for (;;) {
        if (!lire_ligne(invite, buf, sizeof buf)) return 0;
        x = strtol(buf, &fin, 10);
        if (fin != buf && *fin == '\0' && x >= min && x <= max) { *v = (int)x; return 1; }
        printf("  Valeur invalide : entier entre %d et %d attendu.\n", min, max);
    }
}

static int lire_reel(const char *invite, double min, double max, double *v)
{
    char buf[64], *fin, *p;
    double x;
    for (;;) {
        if (!lire_ligne(invite, buf, sizeof buf)) return 0;
        for (p = buf; *p; p++) if (*p == ',') *p = '.';    /* accepte 12,5 */
        x = strtod(buf, &fin);
        if (fin != buf && *fin == '\0' && x >= min && x <= max) { *v = x; return 1; }
        printf("  Valeur invalide : nombre entre %.2f et %.2f attendu.\n", min, max);
    }
}

/* ------------------------------------------------------------------------- */
/* Mesure d'une opération non destructrice (pour l'affichage dans le menu)    */
/* ------------------------------------------------------------------------- */

typedef struct { int st, cle, k, methode; Etudiant *sortie; long long puits; } CtxMenu;

static double chrono_us(void (*op)(CtxMenu *), CtxMenu *c)
{
    clock_t debut = clock(), fin;
    long n = 0;
    do { op(c); n++; fin = clock(); } while (fin - debut < CLOCKS_PER_SEC / 20);  /* >= 50 ms */
    return (double)(fin - debut) * 1e6 / CLOCKS_PER_SEC / n;
}

static void op_rech(CtxMenu *c)  { c->puits += structure_rechercher(&g_annuaire.s[c->st], c->cle); }
static void op_cpt(CtxMenu *c)   { c->puits += structure_compter(&g_annuaire.s[c->st], c->cle); }
static void op_trie(CtxMenu *c)  { c->puits += structure_trie(&g_annuaire.s[c->st], c->sortie, g_mode_pivot); }
static void op_topk(CtxMenu *c)  { c->puits += annuaire_topk(&g_annuaire, c->methode, c->k, c->sortie); }

/* ------------------------------------------------------------------------- */

static void afficher_liste(const Etudiant *t, int n, int max)
{
    int i;
    if (n == 0) { printf("  (aucun etudiant)\n"); return; }
    etudiant_afficher_entete(stdout);
    for (i = 0; i < n && (max <= 0 || i < max); i++) etudiant_afficher(stdout, &t[i]);
    if (max > 0 && n > max) printf("  ... (%d etudiants non affiches)\n", n - max);
}

static int premiere_structure(void) { return g_active < 0 ? 0 : g_active; }
static int derniere_structure(void) { return g_active < 0 ? NB_STRUCTURES - 1 : g_active; }

static void menu_choisir_structure(void)
{
    int i, c;
    printf("\n  Structures disponibles :\n");
    for (i = 0; i < NB_STRUCTURES; i++) printf("   %d. %s\n", i + 1, structure_nom(i));
    printf("   5. Toutes (comparaison)\n");
    if (lire_entier("  Choix : ", 1, 5, &c)) g_active = c == 5 ? -1 : c - 1;
}

static void menu_ajouter(void)
{
    char nom[128], prenom[128], sexe[16];
    float notes[NB_MATIERES];
    int age, i, err;
    double x;
    Etudiant e;
    printf("\n  --- Ajout d'un etudiant (dans les 4 structures) ---\n");
    if (!lire_ligne("  Nom    : ", nom, sizeof nom)) return;
    if (!lire_ligne("  Prenom : ", prenom, sizeof prenom)) return;
    if (!lire_entier("  Age    : ", AGE_MIN, AGE_MAX, &age)) return;
    do {
        if (!lire_ligne("  Sexe (M/F) : ", sexe, sizeof sexe)) return;
    } while (strlen(sexe) != 1 || !strchr("MmFf", sexe[0]));
    for (i = 0; i < NB_MATIERES; i++) {
        char inv[64];
        snprintf(inv, sizeof inv, "  Note %-14s : ", NOMS_MATIERES[i]);
        if (!lire_reel(inv, 0.0, 20.0, &x)) return;
        notes[i] = (float)x;
    }
    err = etudiant_remplir(&e, nom, prenom, age, sexe[0], notes);
    if (err != ETU_OK) { printf("  Erreur : %s\n", etudiant_message_erreur(err)); return; }
    e.id = etudiant_nouvel_id();
    if (!annuaire_ajouter(&g_annuaire, &e)) { printf("  Erreur : memoire insuffisante\n"); return; }
    printf("  Etudiant ajoute : matricule %d, moyenne %.2f\n", e.id, e.cle / 100.0);
}

static int lire_moyenne(int *cle)
{
    double m;
    if (!lire_reel("  Moyenne recherchee (0-20) : ", 0.0, 20.0, &m)) return 0;
    *cle = cle_depuis_moyenne(m);
    return 1;
}

static void menu_rechercher(void)
{
    int cle, s;
    CtxMenu c;
    if (!lire_moyenne(&cle)) return;
    memset(&c, 0, sizeof c);
    c.cle = cle;
    printf("\n  %-42s %-9s %-8s %14s %14s\n", "Structure", "Existe", "Nombre", "t recherche", "t comptage");
    for (s = premiere_structure(); s <= derniere_structure(); s++) {
        int existe = structure_rechercher(&g_annuaire.s[s], cle);
        int nb = structure_compter(&g_annuaire.s[s], cle);
        double t1, t2;
        c.st = s;
        t1 = chrono_us(op_rech, &c);
        t2 = chrono_us(op_cpt, &c);
        printf("  %-42s %-9s %-8d %11.3f us %11.3f us\n", structure_nom(s), existe ? "oui" : "non", nb, t1, t2);
    }
    if (structure_compter(&g_annuaire.s[ST_S2_TRIE], cle) > 0) {
        /* liste des étudiants ayant cette moyenne (via la dichotomie de S2) */
        const S2Tableau *s2 = &g_annuaire.s[ST_S2_TRIE].u.s2;
        int d = s2_borne_inf(s2, cle), f = s2_borne_sup(s2, cle);
        printf("\n  Etudiants ayant la moyenne %.2f :\n", cle / 100.0);
        afficher_liste(s2->t + d, f - d, 50);
    }
}

static void menu_supprimer(void)
{
    int cle, id, nb;
    Etudiant sup;
    if (!lire_moyenne(&cle)) return;
    nb = structure_compter(&g_annuaire.s[ST_S2_TRIE], cle);
    if (nb == 0) { printf("  Aucun etudiant avec la moyenne %.2f\n", cle / 100.0); return; }
    id = -1;
    if (nb > 1) {
        const S2Tableau *s2 = &g_annuaire.s[ST_S2_TRIE].u.s2;
        int d = s2_borne_inf(s2, cle);
        printf("  %d etudiants ont cette moyenne :\n", nb);
        afficher_liste(s2->t + d, nb, 50);
        if (!lire_entier("  Matricule a supprimer (0 = le premier arrive) : ", 0, 1 << 30, &id)) return;
        if (id == 0) id = -1;
    }
    /* cas de l'ABR (feuille / un fils / deux fils) : on le détermine sur une copie */
    {
        Structure copie;
        int cas = -1, idc = id;
        if (idc < 0) {
            const S1Tableau *s1 = &g_annuaire.s[ST_S1_TABLEAU].u.s1t;
            idc = s1->t[s1t_rechercher(s1, cle)].id;
        }
        if (structure_copier(&copie, &g_annuaire.s[ST_S3_ABR])) {
            structure_supprimer(&copie, cle, idc, NULL, &cas);
            structure_detruire(&copie);
        }
        if (annuaire_supprimer(&g_annuaire, cle, id, &sup)) {
            static const char *CAS[] = {"feuille", "noeud a un fils", "noeud a deux fils (successeur)"};
            printf("  Supprime des 4 structures : ");
            etudiant_afficher(stdout, &sup);
            if (cas >= 0) printf("  Cas de suppression dans l'ABR : %s\n", CAS[cas]);
        } else printf("  Matricule introuvable pour cette moyenne.\n");
    }
}

static void menu_afficher_trie(void)
{
    int n = annuaire_taille(&g_annuaire), max, s;
    Etudiant *t;
    CtxMenu c;
    if (n == 0) { printf("  Base vide.\n"); return; }
    if (!lire_entier("  Nombre de lignes a afficher (0 = toutes) : ", 0, n, &max)) return;
    t = (Etudiant *)MALLOC((size_t)n * sizeof *t);
    if (!t) return;
    memset(&c, 0, sizeof c);
    c.sortie = t;
    for (s = premiere_structure(); s <= derniere_structure(); s++) {
        c.st = s;
        structure_trie(&g_annuaire.s[s], t, g_mode_pivot);
        printf("\n  == %s ==  (production de la sequence triee : %.3f us)\n", structure_nom(s), chrono_us(op_trie, &c));
        if (g_active >= 0 || s == derniere_structure()) afficher_liste(t, n, max);
    }
    FREE(t);
}

static void menu_topk(int avec_tas)
{
    int n = annuaire_taille(&g_annuaire), k, m, m0, m1;
    Etudiant *t;
    CtxMenu c;
    if (n == 0) { printf("  Base vide.\n"); return; }
    if (!lire_entier("  k = ", 1, n, &k)) return;
    t = (Etudiant *)MALLOC((size_t)k * sizeof *t);
    if (!t) return;
    memset(&c, 0, sizeof c);
    c.sortie = t;
    c.k = k;
    m0 = avec_tas ? 0 : premiere_structure();
    m1 = avec_tas ? METHODE_TAS : derniere_structure();
    for (m = m0; m <= m1; m++) {
        c.methode = m;
        annuaire_topk(&g_annuaire, m, k, t);
        printf("\n  == %s ==  temps moyen : %.3f us\n", structure_nom(m), chrono_us(op_topk, &c));
        if (m == m1) afficher_liste(t, k, 30);
    }
    if (avec_tas) printf("\n  Complexites : S1 Θ(n log n) (tri rapide) ; S2 Θ(k) ; S3 Θ(h + k) ; tas Θ(n + k log n).\n");
    FREE(t);
}

static void menu_generer(void)
{
    int n, mode;
    clock_t t0;
    if (!lire_entier("  Nombre d'etudiants n (1 - 200000) : ", 1, 200000, &n)) return;
    if (!lire_entier("  Ordre d'arrivee : 0 aleatoire, 1 croissant, 2 decroissant : ", 0, 2, &mode)) return;
    t0 = clock();
    if (annuaire_generer(&g_annuaire, n, mode))
        printf("  %d etudiants generes et inseres dans les 4 structures (%.2f s).\n",
               n, (double)(clock() - t0) / CLOCKS_PER_SEC);
    else printf("  Erreur : memoire insuffisante.\n");
}

static void menu_detail(void)
{
    int id, i;
    Etudiant e;
    if (!lire_entier("  Matricule : ", 1, 1 << 30, &id)) return;
    if (!annuaire_trouver_id(&g_annuaire, id, &e)) { printf("  Matricule inconnu.\n"); return; }
    printf("\n  Matricule : %d\n  Nom       : %s\n  Prenom    : %s\n  Age       : %d\n  Sexe      : %c\n",
           e.id, e.nom, e.prenom, e.age, e.sexe);
    for (i = 0; i < NB_MATIERES; i++) printf("  %-14s: %5.2f / 20\n", NOMS_MATIERES[i], e.notes[i]);
    printf("  Moyenne   : %.2f / 20\n", e.cle / 100.0);
}

static void menu_infos(void)
{
    int s;
    AbrStats st;
    printf("\n  %-42s %8s %12s\n", "Structure", "Taille", "Memoire");
    for (s = 0; s < NB_STRUCTURES; s++)
        printf("  %-42s %8d %9.1f Ko\n", structure_nom(s), structure_taille(&g_annuaire.s[s]),
               structure_memoire(&g_annuaire.s[s]) / 1024.0);
    abr_statistiques(&g_annuaire.s[ST_S3_ABR].u.s3, &st);
    printf("\n  ABR : hauteur %d (minimum possible %d), sous-arbre gauche %d, droit %d,\n"
           "        %d feuilles, profondeur moyenne %.2f\n",
           st.hauteur, st.hauteur_min, st.hauteur_gauche, st.hauteur_droit, st.nb_feuilles, st.profondeur_moyenne);
}

/* Bonus 2 : construction classique (moyennes croissantes) vs équilibrée. */
static void menu_bonus_abr(void)
{
    int n;
    Etudiant *t;
    ABR a, b;
    clock_t t0;
    double tc, te;
    long rep;
    if (!lire_entier("  n (100 - 50000) : ", 100, 50000, &n)) return;
    t = (Etudiant *)MALLOC((size_t)n * sizeof *t);
    if (!t) return;
    generer_jeu(t, n, GEN_CROISSANT);
    rep = 0; t0 = clock();
    do { abr_init(&a); abr_construire_sequentiel(&a, t, n); rep++;
         if (clock() - t0 < CLOCKS_PER_SEC / 10) detruire_arbre(&a); else break; } while (1);
    tc = (double)(clock() - t0) * 1e3 / CLOCKS_PER_SEC / rep;
    rep = 0; t0 = clock();
    do { abr_init(&b); abr_construire_equilibre(&b, t, n); rep++;
         if (clock() - t0 < CLOCKS_PER_SEC / 10) detruire_arbre(&b); else break; } while (1);
    te = (double)(clock() - t0) * 1e3 / CLOCKS_PER_SEC / rep;
    printf("\n  %-46s %10s %12s\n", "Construction a partir de moyennes triees", "Hauteur", "Temps");
    printf("  %-46s %10d %9.3f ms\n", "ABR classique (insertions croissantes)", abr_hauteur(&a), tc);
    printf("  %-46s %10d %9.3f ms\n", "ABR equilibre (milieu d'abord, inserer_abr)", abr_hauteur(&b), te);
    {
        AbrStats st;
        abr_statistiques(&b, &st);
        printf("  Hauteur minimale theorique : %d (ceil(log2(n+1)))\n", st.hauteur_min);
    }
    detruire_arbre(&a);
    detruire_arbre(&b);
    FREE(t);
}

static void menu_sauver(void)
{
    char nom[256];
    FILE *f;
    const S1Tableau *s1 = &g_annuaire.s[ST_S1_TABLEAU].u.s1t;
    int i;
    if (!lire_ligne("  Fichier de sortie : ", nom, sizeof nom) || !nom[0]) return;
    f = fopen(nom, "w");
    if (!f) { printf("  Impossible d'ouvrir %s\n", nom); return; }
    for (i = 0; i < s1->n; i++) {
        const Etudiant *e = &s1->t[i];
        fprintf(f, "%s;%s;%d;%c;%.2f;%.2f;%.2f;%.2f;%.2f\n", e->nom, e->prenom, e->age, e->sexe,
                e->notes[0], e->notes[1], e->notes[2], e->notes[3], e->notes[4]);
    }
    fclose(f);
    printf("  %d etudiants sauvegardes.\n", s1->n);
}

static void menu_charger(void)
{
    char nom[256], ligne[512];
    FILE *f;
    int lus = 0, rejets = 0;
    if (!lire_ligne("  Fichier a charger (nom;prenom;age;sexe;n1;n2;n3;n4;n5) : ", nom, sizeof nom) || !nom[0]) return;
    f = fopen(nom, "r");
    if (!f) { printf("  Impossible d'ouvrir %s\n", nom); return; }
    while (fgets(ligne, sizeof ligne, f)) {
        char n1[64], p1[64], sx;
        int age;
        float no[NB_MATIERES];
        Etudiant e;
        if (sscanf(ligne, "%63[^;];%63[^;];%d;%c;%f;%f;%f;%f;%f", n1, p1, &age, &sx,
                   &no[0], &no[1], &no[2], &no[3], &no[4]) == 9 &&
            etudiant_remplir(&e, n1, p1, age, sx, no) == ETU_OK) {
            e.id = etudiant_nouvel_id();
            annuaire_ajouter(&g_annuaire, &e);
            lus++;
        } else rejets++;
    }
    fclose(f);
    printf("  %d etudiants ajoutes, %d lignes rejetees.\n", lus, rejets);
}

static void menu_bench(int rapide)
{
    ConfigBench c;
    if (rapide) bench_config_rapide(&c);
    else bench_config_defaut(&c);
    printf("  Etude %s : resultats dans resultats/, courbes dans graphiques/.\n", rapide ? "rapide" : "complete");
    bench_executer(&c, stdout);
}

static void afficher_menu(void)
{
    printf("\n==================================================================\n");
    printf("  GESTIONNAIRE D'ANNUAIRE D'ETUDIANTS - Mini-projet A (2026/2027)\n");
    printf("  Base : %d etudiants | Structure active : %s\n", annuaire_taille(&g_annuaire),
           g_active < 0 ? "toutes (comparaison)" : structure_nom(g_active));
    printf("==================================================================\n");
    printf("   1. Choisir la structure active (S1 / S2 / S3 / toutes)\n");
    printf("   2. Ajouter un etudiant\n");
    printf("   3. Rechercher par moyenne (existence + nombre d'etudiants)\n");
    printf("   4. Supprimer un etudiant\n");
    printf("   5. Afficher tous les etudiants par moyenne croissante\n");
    printf("   6. Classement des k meilleurs etudiants\n");
    printf("   7. Generer une base aleatoire de n etudiants\n");
    printf("   8. Detail d'un etudiant (matricule)\n");
    printf("   9. Informations : tailles, memoire, hauteur de l'ABR\n");
    printf("  10. Bonus 1 : top-k par tas max vs les 3 structures\n");
    printf("  11. Bonus 2 : ABR equilibre vs ABR classique (pire cas)\n");
    printf("  12. Etude experimentale complete (CSV + gnuplot)\n");
    printf("  13. Etude experimentale rapide\n");
    printf("  14. Relancer gnuplot sur les derniers resultats\n");
    printf("  15. Sauvegarder la base dans un fichier texte\n");
    printf("  16. Charger des etudiants depuis un fichier texte\n");
    printf("   0. Quitter\n");
}

static int analyser_tailles(const char *s, ConfigBench *c)
{
    int n = 0;
    while (*s && n < BENCH_MAX_TAILLES) {
        char *fin;
        long v = strtol(s, &fin, 10);
        if (fin == s || v < 10 || v > 1000000) return 0;
        c->tailles[n++] = (int)v;
        s = (*fin == ',') ? fin + 1 : fin;
        if (*fin && *fin != ',') return 0;
    }
    c->nb_tailles = n;
    return n > 0;
}

int main(int argc, char **argv)
{
    int i, choix, bench = 0, rapide = 0, gp = 0;
    ConfigBench cfg;
#ifdef _WIN32
    SetConsoleOutputCP(CP_UTF8);
    SetConsoleCP(CP_UTF8);
#endif
    bench_config_defaut(&cfg);
    for (i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--bench")) bench = 1;
        else if (!strcmp(argv[i], "--rapide")) rapide = 1;
        else if (!strcmp(argv[i], "--gnuplot")) gp = 1;
        else if (!strcmp(argv[i], "--sans-gnuplot")) cfg.gnuplot = 0;
        else if (!strcmp(argv[i], "--dossier") && i + 1 < argc) {
            if (changer_dossier(argv[++i]) != 0) { fprintf(stderr, "Dossier introuvable : %s\n", argv[i]); return 1; }
        }
        else if (!strcmp(argv[i], "--tailles") && i + 1 < argc) {
            if (!analyser_tailles(argv[++i], &cfg)) { fprintf(stderr, "Tailles invalides\n"); return 1; }
        }
        else if (!strcmp(argv[i], "--sims") && i + 1 < argc) cfg.nb_simulations = atoi(argv[++i]);
        else if (!strcmp(argv[i], "--seuil") && i + 1 < argc) cfg.seuil_ms = atof(argv[++i]);
        else { fprintf(stderr, "Option inconnue : %s\n", argv[i]); return 1; }
    }
    if (bench) {
        if (rapide) {
            ConfigBench r;
            bench_config_rapide(&r);
            r.gnuplot = cfg.gnuplot;
            cfg = r;
        }
        if (cfg.nb_simulations < 1) cfg.nb_simulations = 1;
        return bench_executer(&cfg, stdout);
    }
    if (gp) return bench_lancer_gnuplot(stdout);

    srand((unsigned)time(NULL));
    annuaire_init(&g_annuaire);
    for (;;) {
        afficher_menu();
        if (!lire_entier("  Votre choix : ", 0, 16, &choix)) break;
        switch (choix) {
        case 0: annuaire_vider(&g_annuaire); printf("  Au revoir.\n"); return 0;
        case 1: menu_choisir_structure(); break;
        case 2: menu_ajouter(); break;
        case 3: menu_rechercher(); break;
        case 4: menu_supprimer(); break;
        case 5: menu_afficher_trie(); break;
        case 6: menu_topk(0); break;
        case 7: menu_generer(); break;
        case 8: menu_detail(); break;
        case 9: menu_infos(); break;
        case 10: menu_topk(1); break;
        case 11: menu_bonus_abr(); break;
        case 12: menu_bench(0); break;
        case 13: menu_bench(1); break;
        case 14: bench_lancer_gnuplot(stdout); break;
        case 15: menu_sauver(); break;
        case 16: menu_charger(); break;
        }
    }
    annuaire_vider(&g_annuaire);
    return 0;
}
