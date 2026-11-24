/*
 * instrument.h — Compteurs d'opérations élémentaires et trace d'exécution.
 *
 * Deux usages :
 *  1) Compteurs (comparaisons, mouvements, nœuds visités) affichés par l'interface
 *     graphique pour chaque opération.
 *  2) Trace : liste d'événements (comparaison, échange, décalage, pivot, ...)
 *     émis PAR LES VRAIES FONCTIONS C pendant leur exécution. L'interface Python
 *     rejoue ces événements pour animer l'algorithme : l'animation reflète donc
 *     exactement l'exécution réelle, pas une simulation écrite en Python.
 *
 * Pour les mesures de temps (programme en ligne de commande / benchmark), le code
 * est compilé avec -DSANS_INSTRUMENTATION : toutes les macros deviennent vides,
 * les algorithmes mesurés ne contiennent alors AUCUNE instruction supplémentaire.
 */
#ifndef INSTRUMENT_H
#define INSTRUMENT_H

/* Types d'événements de trace (dupliqués dans gui/backend.py). */
enum {
    EV_COMPARE = 1,     /* a=i, b=j        : comparaison t[i] / t[j]                   */
    EV_SWAP,            /* a=i, b=j        : échange t[i] <-> t[j]                     */
    EV_SHIFT,           /* a=dst, b=src    : décalage t[dst] = t[src]                  */
    EV_HOLD,            /* a=i, b=clé, c=id: élément « mis de côté » (clé d'insertion)  */
    EV_PLACE,           /* a=i, b=clé, c=id: élément mis de côté écrit en t[i]          */
    EV_PIVOT,           /* a=i, b=clé      : pivot choisi (placé en t[i])               */
    EV_RANGE,           /* a=g, b=d        : sous-tableau traité [g..d]                 */
    EV_SORTED,          /* a=i             : t[i] est à sa place définitive             */
    EV_DICHO,           /* a=g, b=m, c=d   : intervalle de dichotomie et milieu         */
    EV_FOUND,           /* a=indice ou id  : élément trouvé                             */
    EV_NOTFOUND,        /*                 : recherche infructueuse                     */
    EV_NODE_VISIT,      /* a=id, b=clé     : nœud de l'ABR visité                       */
    EV_NODE_INSERT,     /* a=id, b=id parent (-1 racine), c=côté (0 gauche, 1 droit)    */
    EV_DEL_CASE,        /* a=cas (0 feuille, 1 un fils, 2 deux fils), b=id du nœud      */
    EV_SUCC,            /* a=id, b=clé     : nœud visité en cherchant le successeur     */
    EV_NODE_REPLACE,    /* a=id cible, b=id successeur : copie du successeur            */
    EV_NODE_REMOVE,     /* a=id            : nœud physiquement retiré                   */
    EV_HEAPIFY,         /* a=i, b=taille   : appel Entasser(i)                          */
    EV_HEAP_SIZE,       /* a=taille du tas                                              */
    EV_EXTRACT,         /* a=clé, b=id     : extraction du maximum                      */
    EV_BUILD_RANGE,     /* a=g, b=m, c=d   : ABR équilibré, insertion du milieu m       */
    EV_COUNT,           /* a=nombre        : résultat d'un comptage                     */
    EV_PHASE            /* a=code de phase (voir commentaires dans le code)             */
};

typedef struct {
    int type, a, b, c;
} EvenementTrace;

typedef struct {
    long long comparaisons;   /* comparaisons de clés                       */
    long long mouvements;     /* copies / décalages / échanges d'éléments   */
    long long visites;        /* nœuds ou maillons parcourus                */
} Compteurs;

#ifdef SANS_INSTRUMENTATION
  #define CPT_CMP()          ((void)0)
  #define CPT_MOV()          ((void)0)
  #define CPT_VIS()          ((void)0)
  #define TRACE(t, a, b, c)  ((void)0)
#else
  extern Compteurs g_cpt;
  extern int g_trace_actif;
  void trace_ajouter(int type, int a, int b, int c);
  #define CPT_CMP()          (g_cpt.comparaisons++)
  #define CPT_MOV()          (g_cpt.mouvements++)
  #define CPT_VIS()          (g_cpt.visites++)
  #define TRACE(t, a, b, c)  do { if (g_trace_actif) trace_ajouter((t), (a), (b), (c)); } while (0)
#endif

/* Gestion (fonctions toujours présentes, inactives sans instrumentation). */
void compteurs_raz(void);
Compteurs compteurs_lire(void);
void trace_activer(int actif);
void trace_vider(void);
int  trace_taille(void);
int  trace_tronquee(void);
const EvenementTrace *trace_donnees(void);
void trace_liberer(void);

#endif
