/*
 * s1_tableau.h — S1 : liste NON TRIÉE implémentée par un TABLEAU DYNAMIQUE.
 *
 * C'est l'implémentation retenue pour S1 (justification dans le rapport) :
 *  - ajout en fin en Θ(1) amorti (capacité doublée quand le tableau est plein) ;
 *  - accès direct t[i] : le tri rapide (top-k, affichage trié) travaille sur une
 *    simple copie mémoire contiguë ;
 *  - parcours séquentiel très favorable au cache (recherche linéaire rapide).
 * Les étudiants sont rangés dans l'ordre d'arrivée ; la suppression décale les
 * éléments suivants pour CONSERVER cet ordre.
 * Une version liste chaînée (s1_liste.h) est fournie pour l'étude comparative.
 */
#ifndef S1_TABLEAU_H
#define S1_TABLEAU_H

#include <stddef.h>
#include "etudiant.h"

typedef struct {
    Etudiant *t;
    int n;          /* nombre d'étudiants   */
    int capacite;   /* taille allouée       */
} S1Tableau;

void   s1t_init(S1Tableau *s);
void   s1t_detruire(S1Tableau *s);
int    s1t_ajouter(S1Tableau *s, const Etudiant *e);           /* 1 si ok, 0 sinon       Θ(1) amorti */
int    s1t_rechercher(const S1Tableau *s, int cle);            /* indice ou -1          Θ(n)        */
int    s1t_compter(const S1Tableau *s, int cle);               /* nb d'étudiants        Θ(n)        */
/* Supprime l'étudiant de clé `cle` et de matricule `id` (id < 0 : le premier
 * trouvé). Retourne 1 si supprimé (copie dans *supprime si non NULL). Θ(n). */
int    s1t_supprimer(S1Tableau *s, int cle, int id, Etudiant *supprime);
/* Écrit les n étudiants triés par moyenne croissante dans sortie (copie puis
 * tri rapide ; S1 n'est pas modifiée). Θ(n log n) en moyenne. */
int    s1t_trie(const S1Tableau *s, Etudiant *sortie, int mode_pivot);
/* k meilleurs (moyenne décroissante) : copie, tri rapide, lecture des k derniers. */
int    s1t_topk(const S1Tableau *s, int k, Etudiant *sortie, int mode_pivot);
int    s1t_copier(S1Tableau *dst, const S1Tableau *src);
size_t s1t_memoire(const S1Tableau *s);

#endif
