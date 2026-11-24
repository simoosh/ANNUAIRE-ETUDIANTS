/*
 * test_structures.c — Tests de validation des structures et algorithmes.
 *
 * Compilé avec -DSUIVI_MEMOIRE : toute fuite mémoire (bloc non libéré) ou
 * écriture hors bornes sur le tas est détectée et fait échouer les tests.
 *
 * Méthode : on applique les mêmes opérations aléatoires (ajouts, suppressions,
 * recherches, comptages) aux 4 structures et à un modèle de référence naïf
 * (tableau + parcours complet), puis on compare tous les résultats.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../src/annuaire.h"
#include "../src/tris.h"
#include "../src/tas.h"
#include "../src/memoire.h"

static int g_tests = 0, g_echecs = 0;

#define VERIFIER(cond, msg) do { g_tests++; if (!(cond)) { g_echecs++; \
    printf("  ECHEC : %s (ligne %d)\n", msg, __LINE__); } } while (0)

static Etudiant etu(int cle)
{
    Etudiant e;
    etudiant_aleatoire_avec_cle(&e, cle);
    return e;
}

/* ---- Validation des entrées ------------------------------------------------ */
static void test_validation(void)
{
    Etudiant e;
    float ok[5] = {10, 12.5f, 14, 8, 16}, ko[5] = {10, 21, 14, 8, 16};
    printf("[1] Validation des saisies\n");
    VERIFIER(etudiant_remplir(&e, "Benali", "Amine", 20, 'M', ok) == ETU_OK, "saisie valide");
    VERIFIER(e.cle == 1210, "moyenne 12.10 -> cle 1210");
    VERIFIER(etudiant_remplir(&e, "", "Amine", 20, 'M', ok) == ETU_ERR_NOM, "nom vide");
    VERIFIER(etudiant_remplir(&e, "Ben4li", "Amine", 20, 'M', ok) == ETU_ERR_NOM, "chiffre dans le nom");
    VERIFIER(etudiant_remplir(&e, "Benali", "Amine", 12, 'M', ok) == ETU_ERR_AGE, "age");
    VERIFIER(etudiant_remplir(&e, "Benali", "Amine", 20, 'X', ok) == ETU_ERR_SEXE, "sexe");
    VERIFIER(etudiant_remplir(&e, "Benali", "Amine", 20, 'f', ok) == ETU_OK && e.sexe == 'F', "sexe minuscule");
    VERIFIER(etudiant_remplir(&e, "Benali", "Amine", 20, 'M', ko) == ETU_ERR_NOTE, "note > 20");
    VERIFIER(etudiant_remplir(&e, "Un nom beaucoup trop long pour le champ", "A", 20, 'M', ok) == ETU_ERR_NOM,
             "nom trop long");
    VERIFIER(cle_depuis_moyenne(12.345) == 1235 && cle_depuis_moyenne(20.5) == -1, "conversion moyenne/cle");
}

/* ---- Tris et tas ----------------------------------------------------------- */
static void test_tris(void)
{
    int n, mode, i;
    printf("[2] Tri rapide, tri par insertion, tas max\n");
    for (n = 0; n <= 300; n += 37) {
        for (mode = 0; mode < 3; mode++) {
            Etudiant *t = (Etudiant *)MALLOC((size_t)(n + 1) * sizeof *t);
            Etudiant *u = (Etudiant *)MALLOC((size_t)(n + 1) * sizeof *u);
            Etudiant *top = (Etudiant *)MALLOC((size_t)(n + 1) * sizeof *top);
            generer_jeu(t, n, mode);
            for (i = 0; i < n; i += 3) t[i].cle = 1000;          /* nombreux doublons */
            memcpy(u, t, (size_t)n * sizeof *t);
            tri_rapide(u, n, PIVOT_MEDIAN3);
            VERIFIER(est_trie(u, n), "tri rapide median3");
            memcpy(u, t, (size_t)n * sizeof *t);
            tri_rapide(u, n, PIVOT_DERNIER);
            VERIFIER(est_trie(u, n), "tri rapide pivot dernier");
            memcpy(u, t, (size_t)n * sizeof *t);
            tri_insertion(u, n);
            VERIFIER(est_trie(u, n), "tri par insertion");
            memcpy(u, t, (size_t)n * sizeof *t);
            construire_tas_max(u, n);
            VERIFIER(est_tas_max(u, n), "ConstruireTasMax");
            if (n > 0) {
                int k = n < 10 ? n : 10, ok = 1;
                Etudiant *ref = (Etudiant *)MALLOC((size_t)n * sizeof *ref);
                memcpy(ref, t, (size_t)n * sizeof *t);
                tri_rapide(ref, n, PIVOT_MEDIAN3);
                VERIFIER(topk_tas(t, n, k, top) == k, "topk_tas nombre");
                for (i = 0; i < k; i++)
                    if (comparer_etudiants(&top[i], &ref[n - 1 - i]) != 0) ok = 0;
                VERIFIER(ok, "topk_tas = k derniers du tableau trie");
                FREE(ref);
            }
            FREE(t); FREE(u); FREE(top);
        }
    }
}

/* ---- Modèle de référence --------------------------------------------------- */
typedef struct { Etudiant t[3000]; int n; } Ref;

static int ref_compter(const Ref *r, int cle)
{
    int i, nb = 0;
    for (i = 0; i < r->n; i++) nb += r->t[i].cle == cle;
    return nb;
}

static void ref_supprimer_id(Ref *r, int id)
{
    int i;
    for (i = 0; i < r->n; i++)
        if (r->t[i].id == id) { r->t[i] = r->t[--r->n]; return; }
}

static void verifier_coherence(const Annuaire *a, const Ref *r, const char *etape)
{
    int s, i;
    char msg[128];
    Etudiant *sortie = (Etudiant *)MALLOC((size_t)(r->n + 1) * sizeof *sortie);
    Etudiant *ref = (Etudiant *)MALLOC((size_t)(r->n + 1) * sizeof *ref);
    memcpy(ref, r->t, (size_t)r->n * sizeof *ref);
    tri_rapide(ref, r->n, PIVOT_MEDIAN3);
    for (s = 0; s < NB_STRUCTURES; s++) {
        int ok = 1;
        snprintf(msg, sizeof msg, "%s : taille %s", etape, structure_nom_court(s));
        VERIFIER(structure_taille(&a->s[s]) == r->n, msg);
        VERIFIER(structure_trie(&a->s[s], sortie, PIVOT_MEDIAN3) == r->n, msg);
        for (i = 0; i < r->n; i++)
            if (sortie[i].cle != ref[i].cle) ok = 0;
        snprintf(msg, sizeof msg, "%s : affichage trie %s", etape, structure_nom_court(s));
        VERIFIER(ok, msg);
    }
    /* S2 trié selon (clé, matricule) et S3 respecte l'invariant */
    VERIFIER(est_trie(a->s[ST_S2_TRIE].u.s2.t, a->s[ST_S2_TRIE].u.s2.n), "S2 reste trie");
    VERIFIER(abr_verifier(&a->s[ST_S3_ABR].u.s3), "ordre ABR (infixe strictement croissant)");
    FREE(sortie);
    FREE(ref);
}

static void test_operations(void)
{
    static Ref r;
    Annuaire a;
    int iter, s, i;
    printf("[3] Operations aleatoires (4 structures vs modele de reference)\n");
    srand(12345);
    annuaire_init(&a);
    r.n = 0;
    for (iter = 0; iter < 4000; iter++) {
        int op = rand() % 10;
        if (op < 5 || r.n == 0) {                       /* ajout (beaucoup de doublons) */
            Etudiant e = etu(800 + rand() % 60);
            if (r.n < 3000) {
                VERIFIER(annuaire_ajouter(&a, &e), "ajout");
                r.t[r.n++] = e;
            }
        } else if (op < 7) {                            /* suppression d'un étudiant précis */
            Etudiant cible = r.t[rand() % r.n], sup;
            VERIFIER(annuaire_supprimer(&a, cible.cle, cible.id, &sup) && sup.id == cible.id,
                     "suppression par (moyenne, matricule)");
            ref_supprimer_id(&r, cible.id);
        } else {                                        /* recherche + comptage */
            int cle = 790 + rand() % 80, attendu = ref_compter(&r, cle);
            for (s = 0; s < NB_STRUCTURES; s++) {
                VERIFIER(structure_rechercher(&a.s[s], cle) == (attendu > 0), "existence");
                VERIFIER(structure_compter(&a.s[s], cle) == attendu, "comptage des doublons");
            }
        }
        if (iter % 500 == 0) verifier_coherence(&a, &r, "en cours");
    }
    verifier_coherence(&a, &r, "final");

    /* top-k : toutes les méthodes donnent les mêmes moyennes */
    {
        Etudiant ref[50], top[50];
        int k = 25, m, ok;
        annuaire_topk(&a, ST_S2_TRIE, k, ref);
        for (m = 0; m <= METHODE_TAS; m++) {
            ok = annuaire_topk(&a, m, k, top) == k;
            for (i = 0; i < k && ok; i++) if (top[i].cle != ref[i].cle) ok = 0;
            VERIFIER(ok, structure_nom_court(m));
        }
        for (i = 1; i < k; i++) VERIFIER(ref[i - 1].cle >= ref[i].cle, "top-k decroissant");
    }

    /* suppression sans matricule : le même étudiant disparaît partout */
    if (r.n > 0) {
        int cle = r.t[0].cle;
        Etudiant sup;
        VERIFIER(annuaire_supprimer(&a, cle, -1, &sup), "suppression par moyenne seule");
        ref_supprimer_id(&r, sup.id);
        verifier_coherence(&a, &r, "apres suppression par moyenne");
    }
    VERIFIER(!annuaire_supprimer(&a, 1999, -1, NULL), "suppression d'une moyenne absente");
    annuaire_vider(&a);
}

/* ---- Les trois cas de suppression de l'ABR -------------------------------- */
static void test_abr_cas(void)
{
    ABR a;
    int cles[] = {1000, 500, 1500, 250, 750, 1250, 1750, 700, 1800, 1500};
    int ids[10], i, cas;
    Etudiant e, sup;
    printf("[4] ABR : trois cas de suppression, doublons, hauteur\n");
    abr_init(&a);
    for (i = 0; i < 10; i++) { e = etu(cles[i]); ids[i] = e.id; inserer_abr(&a, &e); }
    /*            1000
     *         /        \
     *       500        1500
     *      /   \      /    \
     *    250   750  1250   1750
     *          /           /    \
     *        700         1500  1800    (doublon 15.00 : matricule plus grand -> droite, puis à gauche de 17.50) */
    VERIFIER(abr_compter(&a, 1500) == 2, "deux etudiants a 15.00");
    VERIFIER(abr_hauteur(&a) == 4, "hauteur 4");
    VERIFIER(abr_supprimer(&a, 250, -1, &sup, &cas) && cas == 0, "cas feuille");
    VERIFIER(abr_supprimer(&a, 750, -1, &sup, &cas) && cas == 1, "cas un fils");
    VERIFIER(abr_supprimer(&a, 1000, -1, &sup, &cas) && cas == 2, "cas deux fils (racine)");
    VERIFIER(a.racine->e.cle == 1250, "successeur 12.50 remonte a la racine");
    VERIFIER(abr_verifier(&a), "invariant apres suppressions");
    VERIFIER(abr_compter(&a, 1500) == 2, "doublons conserves");
    VERIFIER(abr_supprimer(&a, 1500, ids[9], &sup, &cas) && sup.id == ids[9], "suppression du doublon precis");
    VERIFIER(abr_compter(&a, 1500) == 1 && abr_verifier(&a), "un seul 15.00 restant");
    VERIFIER(!abr_supprimer(&a, 1, -1, &sup, &cas), "absent");
    detruire_arbre(&a);
    VERIFIER(a.racine == NULL && a.n == 0, "detruire_arbre");
}

/* ---- ABR dégénéré et ABR équilibré (bonus 2) ------------------------------ */
static void test_abr_formes(void)
{
    int n = 20000;
    Etudiant *t = (Etudiant *)MALLOC((size_t)n * sizeof *t), *sortie;
    ABR deg, equi, copie;
    AbrStats st;
    printf("[5] ABR degenere (20000 noeuds) vs equilibre, copie, parcours\n");
    generer_jeu(t, n, GEN_CROISSANT);
    abr_init(&deg); abr_init(&equi);
    abr_construire_sequentiel(&deg, t, n);
    abr_construire_equilibre(&equi, t, n);
    VERIFIER(abr_hauteur(&deg) == n, "insertion croissante -> peigne de hauteur n");
    abr_statistiques(&equi, &st);
    printf("    hauteur equilibre = %d (minimum %d), degenere = %d\n", st.hauteur, st.hauteur_min, n);
    VERIFIER(st.hauteur <= st.hauteur_min + 6, "ABR equilibre de hauteur ~ log2(n)");
    VERIFIER(abr_verifier(&deg) && abr_verifier(&equi), "invariants");
    sortie = (Etudiant *)MALLOC((size_t)n * sizeof *sortie);
    VERIFIER(abr_trie(&deg, sortie) == n && est_trie(sortie, n), "infixe sur peigne (pile explicite)");
    VERIFIER(abr_copier(&copie, &deg) && copie.n == n && abr_hauteur(&copie) == n, "copie du peigne");
    VERIFIER(abr_topk(&deg, 10, sortie) == 10 && sortie[0].cle == t[n - 1].cle, "top-k sur peigne");
    detruire_arbre(&copie);
    detruire_arbre(&deg);
    detruire_arbre(&equi);
    FREE(sortie);
    FREE(t);
}

/* ---- Pires/meilleurs cas S2 (comptage des mouvements via la structure) ---- */
static void test_s2_cas(void)
{
    S2Tableau s;
    int i;
    Etudiant e;
    printf("[6] S2 : insertion croissante / decroissante, dichotomie\n");
    s2_init(&s);
    for (i = 0; i < 1000; i++) { e = etu(i * 2); s2_ajouter(&s, &e); }
    VERIFIER(est_trie(s.t, s.n), "S2 insertion croissante");
    VERIFIER(s2_rechercher(&s, 998) >= 0 && s2_rechercher(&s, 999) < 0, "dichotomie");
    VERIFIER(s2_compter(&s, 0) == 1 && s2_borne_inf(&s, 1) == 1, "bornes");
    s2_detruire(&s);
    for (i = 999; i >= 0; i--) { e = etu(i); s2_ajouter(&s, &e); }
    VERIFIER(est_trie(s.t, s.n), "S2 insertion decroissante");
    s2_detruire(&s);
}

int main(void)
{
    printf("=== Tests du mini-projet A ===\n");
    srand(2026);
    test_validation();
    test_tris();
    test_operations();
    test_abr_cas();
    test_abr_formes();
    test_s2_cas();
    printf("[7] Memoire : blocs non liberes = %ld, debordements detectes = %ld\n",
           mem_blocs_vivants(), mem_erreurs());
    VERIFIER(mem_blocs_vivants() == 0, "aucune fuite memoire");
    VERIFIER(mem_erreurs() == 0, "aucun acces hors bornes detecte");
    printf("=== %d verifications, %d echec(s) ===\n", g_tests, g_echecs);
    return g_echecs ? 1 : 0;
}
