/*
 * s2_trie.h — S2 : TABLEAU TRIÉ par moyenne croissante.
 *
 *  - Ajout : principe du tri par insertion (inserer_dans_trie de tris.c) :
 *    décalage vers la droite des éléments plus grands. Θ(1) au mieux (nouvel
 *    élément plus grand que tous), Θ(n) au pire (plus petit que tous).
 *  - Recherche : dichotomie (TP1). Existence Θ(1) au mieux, Θ(log n) au pire ;
 *    comptage par deux dichotomies (bornes inférieure et supérieure) Θ(log n).
 *  - Suppression : dichotomie + décalage à gauche, l'ordre est conservé.
 *  - Top-k : lecture directe des k derniers, Θ(k).
 * Ordre interne : (clé, matricule) — à moyenne égale, ordre d'arrivée.
 */
#ifndef S2_TRIE_H
#define S2_TRIE_H

#include <stddef.h>
#include "etudiant.h"

typedef struct {
    Etudiant *t;
    int n;
    int capacite;
} S2Tableau;

void   s2_init(S2Tableau *s);
void   s2_detruire(S2Tableau *s);
int    s2_ajouter(S2Tableau *s, const Etudiant *e);        /* 1 si ok             */
int    s2_rechercher(const S2Tableau *s, int cle);         /* indice ou -1 (dichotomie) */
int    s2_borne_inf(const S2Tableau *s, int cle);          /* 1er indice de clé >= cle  */
int    s2_borne_sup(const S2Tableau *s, int cle);          /* 1er indice de clé >  cle  */
int    s2_compter(const S2Tableau *s, int cle);            /* Θ(log n)            */
int    s2_supprimer(S2Tableau *s, int cle, int id, Etudiant *supprime);
int    s2_trie(const S2Tableau *s, Etudiant *sortie);      /* déjà trié : Θ(n)    */
int    s2_topk(const S2Tableau *s, int k, Etudiant *sortie); /* Θ(k)             */
int    s2_copier(S2Tableau *dst, const S2Tableau *src);
size_t s2_memoire(const S2Tableau *s);

#endif
