/*
 * tris.h — Algorithmes de tri du TP2, écrits par le groupe (pas de qsort).
 *
 *  - tri_rapide       : tri rapide (partition de Lomuto), utilisé par S1 pour
 *                       l'affichage trié et le top-k.
 *  - inserer_dans_trie: étape élémentaire du tri par insertion ; c'est EXACTEMENT
 *                       la fonction utilisée par S2 pour insérer en gardant l'ordre.
 *  - tri_insertion    : tri par insertion complet (enchaîne inserer_dans_trie).
 *
 * L'ordre utilisé est l'ordre total (clé, matricule) de comparer_etudiants() :
 * les doublons de moyenne sont donc départagés par le matricule, ce qui évite la
 * dégradation du tri rapide en présence de nombreuses moyennes identiques.
 */
#ifndef TRIS_H
#define TRIS_H

#include "etudiant.h"

enum {
    PIVOT_MEDIAN3 = 0,   /* médiane de (premier, milieu, dernier) : défaut   */
    PIVOT_DERNIER = 1    /* dernier élément (version classique du cours)     */
};

/* Tri rapide en place de t[0..n-1].
 * Complexité : Θ(n log n) en moyenne ; Θ(n²) au pire (ex. PIVOT_DERNIER sur un
 * tableau déjà trié). La récursion se fait sur la plus petite partie et une
 * boucle traite la plus grande : profondeur de pile O(log n) même au pire cas. */
void tri_rapide(Etudiant *t, int n, int mode_pivot);

/* t[0..n-1] est trié, t a de la place pour n+1 éléments.
 * Insère *x à sa place en décalant vers la droite les éléments plus grands.
 * Retourne la position d'insertion. Θ(1) au mieux, Θ(n) au pire. */
int  inserer_dans_trie(Etudiant *t, int n, const Etudiant *x);

/* Tri par insertion en place. Θ(n) au mieux (déjà trié), Θ(n²) au pire. */
void tri_insertion(Etudiant *t, int n);

/* Vérifie que t est trié selon (clé, matricule) ; 1 si oui. */
int  est_trie(const Etudiant *t, int n);

#endif
