/*
 * instrument.c — Tampon de trace et compteurs (voir instrument.h).
 */
#include "instrument.h"
#include "memoire.h"

#define TRACE_MAX 400000          /* au-delà, la trace est tronquée */

Compteurs g_cpt = {0, 0, 0};
int g_trace_actif = 0;

static EvenementTrace *g_trace = NULL;
static int g_taille = 0, g_capacite = 0, g_tronquee = 0;

void trace_ajouter(int type, int a, int b, int c)
{
    if (g_taille >= g_capacite) {
        int nc;
        EvenementTrace *n;
        if (g_capacite >= TRACE_MAX) { g_tronquee = 1; return; }
        nc = g_capacite ? 2 * g_capacite : 1024;
        if (nc > TRACE_MAX) nc = TRACE_MAX;
        n = (EvenementTrace *)REALLOC(g_trace, (size_t)nc * sizeof *n);
        if (!n) { g_tronquee = 1; return; }
        g_trace = n;
        g_capacite = nc;
    }
    g_trace[g_taille].type = type;
    g_trace[g_taille].a = a;
    g_trace[g_taille].b = b;
    g_trace[g_taille].c = c;
    g_taille++;
}

void compteurs_raz(void)
{
    g_cpt.comparaisons = g_cpt.mouvements = g_cpt.visites = 0;
}

Compteurs compteurs_lire(void) { return g_cpt; }

void trace_activer(int actif) { g_trace_actif = actif; }
void trace_vider(void)        { g_taille = 0; g_tronquee = 0; }
int  trace_taille(void)       { return g_taille; }
int  trace_tronquee(void)     { return g_tronquee; }
const EvenementTrace *trace_donnees(void) { return g_trace; }

void trace_liberer(void)
{
    FREE(g_trace);
    g_trace = NULL;
    g_taille = g_capacite = 0;
    g_tronquee = 0;
}
