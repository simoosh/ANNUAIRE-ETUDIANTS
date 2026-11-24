/*
 * benchmark.h — Étude expérimentale : mesures de temps avec clock(), fichiers
 *               CSV et courbes gnuplot lancées par system().
 *
 * PROTOCOLE (détaillé dans le rapport) :
 *  - Jeux de données générés AVANT toute mesure (la génération aléatoire n'est
 *    jamais chronométrée) ; les mêmes jeux servent aux 4 structures.
 *  - Trois jeux par taille n : aléatoire, croissant (mêmes étudiants triés),
 *    décroissant. Les pires/meilleurs cas de chaque structure en découlent.
 *  - Opérations rapides : répétées dans une même fenêtre chronométrée jusqu'à
 *    atteindre un temps cumulé minimal (seuil, 100 ms par défaut), puis
 *    temps moyen = temps cumulé / nombre de répétitions.
 *  - Opérations destructrices (suppression, construction) : la structure est
 *    recopiée (ou détruite) HORS chronométrage avant chaque répétition.
 *  - Moyenne sur plusieurs simulations (jeux aléatoires différents).
 *  - Programme compilé en -O2 avec -DSANS_INSTRUMENTATION : aucune trace ni
 *    compteur dans le code mesuré ; aucune interface graphique pendant la mesure.
 */
#ifndef BENCHMARK_H
#define BENCHMARK_H

#include <stdio.h>

#define BENCH_MAX_TAILLES 16

typedef struct {
    int    tailles[BENCH_MAX_TAILLES];
    int    nb_tailles;
    int    nb_simulations;   /* jeux aléatoires différents par taille          */
    double seuil_ms;         /* temps chronométré cumulé minimal par mesure    */
    double plafond_s;        /* durée réelle maximale d'une mesure             */
    int    k;                /* paramètre du top-k                             */
    int    nb_requetes;      /* requêtes de recherche par lot                  */
    unsigned graine;         /* graine de srand() (reproductibilité)           */
    int    gnuplot;          /* 1 : tracer les courbes avec gnuplot            */
} ConfigBench;

void bench_config_defaut(ConfigBench *c);
void bench_config_rapide(ConfigBench *c);

/* Exécute toute l'étude. Les fichiers sont écrits dans resultats/, gnuplot/ et
 * graphiques/ (relatifs au répertoire courant). Retourne 0 si succès. */
int  bench_executer(const ConfigBench *c, FILE *journal);

/* Relance uniquement gnuplot sur les scripts déjà générés. */
int  bench_lancer_gnuplot(FILE *journal);

#endif
