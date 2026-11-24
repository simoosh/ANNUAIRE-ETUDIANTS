/*
 * tas.h — Tas max (TP3) : Entasser, ConstruireTasMax, extraction du maximum
 *         et top-k par tas (BONUS 1).
 *
 * Représentation : tableau t[0..taille-1], fils gauche de i en 2i+1,
 * fils droit en 2i+2, père en (i-1)/2. Ordre : (clé, matricule).
 */
#ifndef TAS_H
#define TAS_H

#include "etudiant.h"

/* Entasser (« tamiser vers le bas ») le nœud i : les sous-arbres de i sont
 * supposés être des tas max. Θ(log n) au pire. */
void entasser(Etudiant *t, int taille, int i);

/* ConstruireTasMax : appelle Entasser de (n/2 - 1) jusqu'à 0. Θ(n). */
void construire_tas_max(Etudiant *t, int n);

/* Retire et retourne le maximum ; *taille est décrémentée. Θ(log n). */
Etudiant extraire_max(Etudiant *t, int *taille);

/* Top-k par tas : copie des n étudiants de src, ConstruireTasMax puis k
 * extractions. sortie reçoit les k meilleurs par moyenne décroissante.
 * Retourne le nombre d'étudiants écrits (min(k, n)), -1 si mémoire insuffisante.
 * Complexité : Θ(n + k log n). */
int  topk_tas(const Etudiant *src, int n, int k, Etudiant *sortie);

/* Vérifie la propriété de tas max ; 1 si oui. */
int  est_tas_max(const Etudiant *t, int n);

#endif
