/*
 * s1_liste.h — S1 (variante) : liste NON TRIÉE par LISTE SIMPLEMENT CHAÎNÉE.
 *
 * Implémentée pour mesurer « l'effet du choix tableau ou liste chaînée »
 * demandé par le sujet :
 *  - ajout en queue Θ(1) (pointeur de queue, pas de réallocation) ;
 *  - suppression : Θ(1) une fois le maillon trouvé (pas de décalage), donc
 *    meilleur cas Θ(1) (tête) contre Θ(n) pour le tableau ;
 *  - mais parcours par pointeurs (défauts de cache) et +8 octets par étudiant ;
 *  - pas d'accès direct : pour trier on recopie dans un tableau.
 */
#ifndef S1_LISTE_H
#define S1_LISTE_H

#include <stddef.h>
#include "etudiant.h"

typedef struct Maillon {
    Etudiant e;
    struct Maillon *suivant;
} Maillon;

typedef struct {
    Maillon *tete, *queue;
    int n;
} S1Liste;

void   s1l_init(S1Liste *s);
void   s1l_detruire(S1Liste *s);
int    s1l_ajouter(S1Liste *s, const Etudiant *e);            /* Θ(1)                    */
int    s1l_rechercher(const S1Liste *s, int cle);             /* position ou -1, Θ(n)    */
int    s1l_compter(const S1Liste *s, int cle);                /* Θ(n)                    */
int    s1l_supprimer(S1Liste *s, int cle, int id, Etudiant *supprime); /* Θ(1)..Θ(n)    */
int    s1l_trie(const S1Liste *s, Etudiant *sortie, int mode_pivot);   /* copie + tri rapide */
int    s1l_topk(const S1Liste *s, int k, Etudiant *sortie, int mode_pivot);
int    s1l_copier(S1Liste *dst, const S1Liste *src);
size_t s1l_memoire(const S1Liste *s);
/* Copie la liste dans un tableau (ordre d'arrivée), retourne n. */
int    s1l_vers_tableau(const S1Liste *s, Etudiant *sortie);

#endif
