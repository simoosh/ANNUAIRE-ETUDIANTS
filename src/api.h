/*
 * api.h — Fonctions exportées par la bibliothèque partagée (annuaire.dll / .so)
 *         et appelées par l'interface graphique Python via ctypes.
 *
 * RÈGLE : l'interface n'implémente AUCUN algorithme. Chaque opération affichée
 * (ajout, recherche, tri, tas, ABR, ...) est exécutée ici, en C, par les mêmes
 * fonctions que le programme en ligne de commande. Les animations rejouent la
 * trace d'événements émise pendant cette exécution réelle (instrument.h).
 */
#ifndef API_H
#define API_H

#include "etudiant.h"
#include "instrument.h"

#ifdef _WIN32
#define API __declspec(dllexport)
#else
#define API __attribute__((visibility("default")))
#endif

/* ---- annuaire principal (4 structures synchronisées) ---- */
API int    api_version(void);
API int    api_taille_etudiant(void);          /* sizeof(Etudiant) : contrôle côté Python */
API void   api_init(void);
API void   api_liberer(void);
API int    api_taille(void);
API int    api_generer(int n, int mode, unsigned graine);
API int    api_ajouter(const char *nom, const char *prenom, int age, char sexe,
                       const float *notes, int trace_structure, int *id);
API const char *api_message_erreur(int code);
API int    api_supprimer(int cle, int id, int trace_structure, Etudiant *supprime, int *cas);
API int    api_rechercher(int s, int cle, int trace);
API int    api_compter(int s, int cle, int trace);
API int    api_trie(int s, Etudiant *sortie, int trace);
API int    api_topk(int methode, int k, Etudiant *sortie, int trace);
API int    api_contenu(int s, Etudiant *sortie);
API int    api_trouver(int id, Etudiant *e);
API double api_memoire(int s);
API void   api_definir_pivot(int mode);
API void   api_abr_stats(int *hauteur, int *hg, int *hd, int *feuilles, int *hmin, double *prof);
API int    api_abr_exporter(int *ids, int *cles, int *fg, int *fd, int max);
/* Temps moyen (µs) d'une opération non destructrice mesuré en C avec clock()
 * (répétitions jusqu'à 50 ms) : op 0 recherche, 1 comptage, 2 tri, 3 top-k. */
API double api_mesurer(int op, int s, int param, long long *reps);

/* ---- compteurs et trace de la dernière opération ---- */
API void   api_compteurs(long long *cmp, long long *mov, long long *vis);
API int    api_trace_taille(void);
API int    api_trace_lire(EvenementTrace *buf, int max);
API int    api_trace_tronquee(void);

/* ---- animations sur données de démonstration (vraies fonctions C) ---- */
API int    api_anim_tri_rapide(const int *cles, int n, int pivot, int *resultat);
API int    api_anim_tri_insertion(const int *cles, int n, int *resultat);
/* Construit un S2 (s2_ajouter) à partir de cles, écrit le tableau trié dans
 * trie, puis trace la recherche (mode 0) ou le comptage (mode 1). */
API int    api_anim_dichotomie(const int *cles, int n, int cle, int mode, int *trie);
API int    api_anim_tas(const int *cles, int n, int k, int *extraits);
API void   api_anim_abr_vider(void);
API int    api_anim_abr_inserer(int cle);
API int    api_anim_abr_sequence(const int *cles, int n, int equilibre);
API int    api_anim_abr_rechercher(int cle);
API int    api_anim_abr_compter(int cle);
API int    api_anim_abr_supprimer(int cle, int *cas);
API int    api_anim_abr_topk(int k, int *cles_sortie);
API int    api_anim_abr_exporter(int *ids, int *cles, int *fg, int *fd, int max);
API int    api_anim_abr_taille(void);
API int    api_anim_abr_hauteur(void);
/* Bonus 2 : n moyennes triées générées en C ; temps (ms, clock()) et hauteurs
 * de l'ABR classique (insertions croissantes) et de l'ABR équilibré. */
API int    api_bench_abr(int n, unsigned graine, double *t_classique, double *t_equilibre,
                         int *h_classique, int *h_equilibre);

#endif
