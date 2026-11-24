/*
 * s3_abr.h — S3 : ARBRE BINAIRE DE RECHERCHE indexé sur la moyenne (TP3).
 *
 * POLITIQUE DES MOYENNES IDENTIQUES (choix du groupe) :
 *   un nœud par étudiant ; l'arbre est ordonné par la moyenne, et deux moyennes
 *   égales sont départagées par le MATRICULE : la clé de l'ABR est le couple
 *   (moyenne, matricule). Il n'y a donc jamais deux clés égales et l'ABR est un
 *   ABR « classique » à clés distinctes. Un étudiant arrivé plus tard (matricule
 *   plus grand) se place à droite des étudiants de même moyenne.
 *   Conséquences :
 *    - recherche par moyenne : on s'arrête au premier nœud de cette moyenne, Θ(h) ;
 *    - les étudiants d'une même moyenne forment un intervalle contigu du parcours
 *      infixe ; le comptage est un parcours élagué en Θ(h + d) (d = nombre trouvé) ;
 *    - la construction « équilibrée » à partir du tableau trié donne une hauteur
 *      minimale même avec beaucoup de doublons (une politique « égal -> droite »
 *      sur la seule moyenne créerait des chaînes de doublons) ;
 *    - le nombre de nœuds est égal au nombre d'étudiants : les expériences
 *      mesurent bien un arbre de taille n ; l'insertion de moyennes triées
 *      produit bien un peigne de hauteur n (ABR dégénéré).
 *   La suppression à deux fils remplace le nœud par son SUCCESSEUR (minimum du
 *   sous-arbre droit).
 *
 * Toutes les opérations sont ITÉRATIVES (ou à pile explicite) : un ABR dégénéré
 * de 20 000 nœuds aurait une profondeur de récursion de 20 000 et ferait
 * déborder la pile d'exécution.
 *
 * Hauteur : nombre de nœuds du plus long chemin racine-feuille (vide = 0).
 */
#ifndef S3_ABR_H
#define S3_ABR_H

#include <stddef.h>
#include "etudiant.h"

typedef struct Noeud {
    Etudiant e;
    struct Noeud *gauche, *droit;
} Noeud;

typedef struct {
    Noeud *racine;
    int n;
} ABR;

typedef struct {
    int hauteur;          /* hauteur de l'arbre                         */
    int hauteur_gauche;   /* hauteur du sous-arbre gauche de la racine  */
    int hauteur_droit;    /* hauteur du sous-arbre droit de la racine   */
    int nb_feuilles;
    int hauteur_min;      /* hauteur minimale possible : ceil(log2(n+1)) */
    double profondeur_moyenne;  /* moyenne des profondeurs (racine = 1) */
} AbrStats;

void   abr_init(ABR *a);
void   detruire_arbre(ABR *a);                         /* Θ(n), sans pile      */
int    inserer_abr(ABR *a, const Etudiant *e);         /* Θ(h)                  */
const Noeud *abr_rechercher(const ABR *a, int cle);    /* premier trouvé, Θ(h)  */
int    abr_compter(const ABR *a, int cle);             /* Θ(h + d)              */
/* Supprime l'étudiant (cle, id) — id < 0 : le premier trouvé sur le chemin.
 * *cas reçoit 0 (feuille), 1 (un fils) ou 2 (deux fils). Retourne 1 si ok. */
int    abr_supprimer(ABR *a, int cle, int id, Etudiant *supprime, int *cas);
int    abr_trie(const ABR *a, Etudiant *sortie);       /* parcours infixe Θ(n)  */
int    abr_topk(const ABR *a, int k, Etudiant *sortie);/* infixe inverse, Θ(h+k)*/
int    abr_hauteur(const ABR *a);
void   abr_statistiques(const ABR *a, AbrStats *st);
int    abr_copier(ABR *dst, const ABR *src);
size_t abr_memoire(const ABR *a);
/* Exporte l'arbre en ordre préfixe : ids, clés, indices des fils (-1 si absent).
 * Retourne le nombre de nœuds écrits (au plus max). */
int    abr_exporter(const ABR *a, int *ids, int *cles, int *fg, int *fd, int max);
/* Vérifie l'ordre (infixe strictement croissant) et le nombre de nœuds. */
int    abr_verifier(const ABR *a);

/* ABR classique : insertions successives de t[0..n-1] dans l'ordre donné. */
void   abr_construire_sequentiel(ABR *a, const Etudiant *t, int n);
/* BONUS 2 — ABR équilibré à partir d'un tableau TRIÉ : insertion (inserer_abr)
 * de l'élément du milieu, puis récursivement du milieu de chaque moitié.
 * Profondeur de récursion log2(n). */
void   abr_construire_equilibre(ABR *a, const Etudiant *tries, int n);

#endif
