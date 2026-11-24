/*
 * annuaire.h — Interface commune aux structures et gestionnaire d'annuaire.
 *
 * Le type Structure regroupe les implémentations (S1 tableau, S1 liste chaînée,
 * S2 tableau trié, S3 ABR) derrière les mêmes opérations. Il est utilisé par :
 *   - le menu en ligne de commande (main.c) ;
 *   - le module d'étude expérimentale (benchmark.c) ;
 *   - la bibliothèque appelée par l'interface graphique (api.c).
 *
 * L'Annuaire contient les quatre structures, remplies avec LES MÊMES étudiants
 * dans le même ordre d'arrivée : chaque opération peut être effectuée et
 * comparée sur chacune d'elles.
 */
#ifndef ANNUAIRE_H
#define ANNUAIRE_H

#include <stddef.h>
#include "etudiant.h"
#include "s1_tableau.h"
#include "s1_liste.h"
#include "s2_trie.h"
#include "s3_abr.h"

enum {
    ST_S1_TABLEAU = 0,     /* S1 : liste non triée (tableau dynamique) — choix retenu */
    ST_S1_LISTE   = 1,     /* S1 : variante liste chaînée (étude comparative)          */
    ST_S2_TRIE    = 2,     /* S2 : tableau trié                                       */
    ST_S3_ABR     = 3,     /* S3 : arbre binaire de recherche                         */
    NB_STRUCTURES = 4,
    METHODE_TAS   = 4      /* top-k par tas max (bonus 1), sur les données de S1      */
};

enum { GEN_ALEATOIRE = 0, GEN_CROISSANT = 1, GEN_DECROISSANT = 2 };

typedef struct {
    int type;
    union {
        S1Tableau s1t;
        S1Liste   s1l;
        S2Tableau s2;
        ABR       s3;
    } u;
} Structure;

const char *structure_nom(int type);
const char *structure_nom_court(int type);
void   structure_init(Structure *s, int type);
void   structure_detruire(Structure *s);
int    structure_ajouter(Structure *s, const Etudiant *e);
int    structure_rechercher(const Structure *s, int cle);      /* 1 si existe, 0 sinon */
int    structure_compter(const Structure *s, int cle);
int    structure_supprimer(Structure *s, int cle, int id, Etudiant *supprime, int *cas);
int    structure_trie(const Structure *s, Etudiant *sortie, int mode_pivot);
int    structure_topk(const Structure *s, int k, Etudiant *sortie, int mode_pivot);
int    structure_copier(Structure *dst, const Structure *src);
int    structure_taille(const Structure *s);
size_t structure_memoire(const Structure *s);
/* Contenu dans l'ordre INTERNE : arrivée (S1), trié (S2), préfixe (S3). */
int    structure_contenu(const Structure *s, Etudiant *sortie);
/* Construit la structure à partir de t[0..n-1] (insertions successives). */
int    structure_construire(Structure *s, const Etudiant *t, int n);

/* ------------------------------------------------------------------------- */

typedef struct {
    Structure s[NB_STRUCTURES];
} Annuaire;

extern int g_mode_pivot;   /* pivot du tri rapide utilisé par S1 (PIVOT_MEDIAN3) */

void annuaire_init(Annuaire *a);
void annuaire_vider(Annuaire *a);
int  annuaire_taille(const Annuaire *a);
/* Ajoute dans les 4 structures ; 1 si succès. */
int  annuaire_ajouter(Annuaire *a, const Etudiant *e);
/* Supprime le même étudiant des 4 structures. id < 0 : le premier étudiant de
 * cette moyenne dans l'ordre d'arrivée. Retourne 1 si supprimé. */
int  annuaire_supprimer(Annuaire *a, int cle, int id, Etudiant *supprime);
/* Top-k par la méthode choisie (0..3 : structure, METHODE_TAS : tas max). */
int  annuaire_topk(const Annuaire *a, int methode, int k, Etudiant *sortie);
/* Recherche un étudiant par matricule (parcours de S1) ; 1 si trouvé. */
int  annuaire_trouver_id(const Annuaire *a, int id, Etudiant *e);
/* Remplace la base par n étudiants générés (mode GEN_*) ; 1 si succès. */
int  annuaire_generer(Annuaire *a, int n, int mode);

/* Génère n étudiants aléatoires dans t ; mode croissant/décroissant : les
 * mêmes étudiants triés par moyenne (tri rapide du groupe). */
void generer_jeu(Etudiant *t, int n, int mode);

#endif
