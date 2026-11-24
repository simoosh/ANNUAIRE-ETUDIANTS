/*
 * memoire.c — Implémentation du suivi mémoire (actif seulement avec -DSUIVI_MEMOIRE).
 */
#include "memoire.h"

#ifdef SUIVI_MEMOIRE
#include <stdio.h>
#include <string.h>
#include <stdint.h>

#define MAGIE    0xC0FFEE11u
#define CANARI   0xA5u
#define NB_CANARI 16

typedef struct {
    size_t   taille;
    uint32_t magie;
    uint32_t pad;          /* garde l'alignement sur 16 octets */
} EnTete;

static long g_vivants = 0;
static long g_erreurs = 0;

static void poser_canari(EnTete *h)
{
    memset((unsigned char *)(h + 1) + h->taille, CANARI, NB_CANARI);
}

static void verifier(EnTete *h)
{
    unsigned char *fin = (unsigned char *)(h + 1) + h->taille;
    int i;
    if (h->magie != MAGIE) {
        fprintf(stderr, "[memoire] ERREUR : bloc invalide ou double libération\n");
        g_erreurs++;
        return;
    }
    for (i = 0; i < NB_CANARI; i++)
        if (fin[i] != CANARI) {
            fprintf(stderr, "[memoire] ERREUR : écriture hors bornes après un bloc de %zu octets\n",
                    h->taille);
            g_erreurs++;
            return;
        }
}

void *mem_malloc(size_t taille)
{
    EnTete *h = (EnTete *)malloc(sizeof(EnTete) + taille + NB_CANARI);
    if (!h) return NULL;
    h->taille = taille;
    h->magie = MAGIE;
    poser_canari(h);
    g_vivants++;
    return h + 1;
}

void mem_free(void *p)
{
    EnTete *h;
    if (!p) return;
    h = (EnTete *)p - 1;
    verifier(h);
    h->magie = 0;          /* détecte une éventuelle double libération */
    g_vivants--;
    free(h);
}

void *mem_realloc(void *p, size_t taille)
{
    EnTete *h, *n;
    if (!p) return mem_malloc(taille);
    h = (EnTete *)p - 1;
    verifier(h);
    n = (EnTete *)realloc(h, sizeof(EnTete) + taille + NB_CANARI);
    if (!n) return NULL;
    n->taille = taille;
    poser_canari(n);
    return n + 1;
}

long mem_blocs_vivants(void) { return g_vivants; }
long mem_erreurs(void)       { return g_erreurs; }

#else
/* Unité de compilation non vide pour les compilateurs stricts. */
typedef int memoire_unite_vide;
#endif
