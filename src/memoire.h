/*
 * memoire.h — Allocation dynamique avec contrôle optionnel des fuites
 *             et des débordements (accès hors bornes) sur le tas.
 *
 * En compilation normale, MALLOC/REALLOC/FREE sont exactement malloc/realloc/free
 * (aucun surcoût pour les mesures de temps).
 *
 * Avec -DSUIVI_MEMOIRE (utilisé par le programme de tests), chaque bloc est
 * entouré d'un en-tête et d'une « sentinelle » (canari) :
 *   - le nombre de blocs vivants permet de détecter les fuites ;
 *   - la sentinelle est vérifiée à chaque libération : toute écriture hors
 *     bornes juste après la fin d'un bloc est détectée.
 */
#ifndef MEMOIRE_H
#define MEMOIRE_H

#include <stdlib.h>

#ifdef SUIVI_MEMOIRE
void *mem_malloc(size_t taille);
void *mem_realloc(void *p, size_t taille);
void  mem_free(void *p);
long  mem_blocs_vivants(void);   /* nombre de blocs alloués non libérés      */
long  mem_erreurs(void);         /* nombre de débordements détectés          */
#define MALLOC(s)     mem_malloc(s)
#define REALLOC(p, s) mem_realloc((p), (s))
#define FREE(p)       mem_free(p)
#else
#define MALLOC(s)     malloc(s)
#define REALLOC(p, s) realloc((p), (s))
#define FREE(p)       free(p)
#endif

#endif
