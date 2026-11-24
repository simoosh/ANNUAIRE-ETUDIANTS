/*
 * etudiant.h — Type Etudiant, calcul de la moyenne, validation, génération aléatoire.
 *
 * CHOIX DE CONCEPTION : la clé de tri et de recherche est la moyenne générale
 * arrondie au centième. Pour éviter les comparaisons de réels (==) peu fiables,
 * elle est aussi stockée sous forme ENTIÈRE dans le champ `cle` (moyenne x 100,
 * de 0 à 2000). Toutes les structures comparent `cle` : les comparaisons sont
 * exactes et deux étudiants affichant la même moyenne (ex. 12.50) ont bien la
 * même clé.
 */
#ifndef ETUDIANT_H
#define ETUDIANT_H

#include <stdio.h>

#define TAILLE_NOM   32      /* chaînes de taille fixe (exigence du sujet) */
#define NB_MATIERES  5
#define CLE_MAX      2000    /* 20.00 en centièmes */
#define AGE_MIN      16
#define AGE_MAX      80

typedef struct {
    int   id;                    /* matricule unique (distingue les doublons de moyenne) */
    char  nom[TAILLE_NOM];
    char  prenom[TAILLE_NOM];
    int   age;
    char  sexe;                  /* 'M' ou 'F' */
    float notes[NB_MATIERES];    /* notes sur 20 */
    float moyenne;               /* moyenne générale arrondie au centième */
    int   cle;                   /* moyenne en centièmes : clé exacte */
} Etudiant;

/* Codes d'erreur de validation */
enum {
    ETU_OK = 0,
    ETU_ERR_NOM,
    ETU_ERR_PRENOM,
    ETU_ERR_AGE,
    ETU_ERR_SEXE,
    ETU_ERR_NOTE
};

extern const char *NOMS_MATIERES[NB_MATIERES];

/* Clé entière (centièmes) d'une moyenne réelle ; -1 si hors [0, 20]. */
int  cle_depuis_moyenne(double moyenne);

/* Calcule moyenne et clé à partir des 5 notes. */
void etudiant_calculer_moyenne(Etudiant *e);

/* Remplit et valide un étudiant ; retourne ETU_OK ou un code d'erreur.
 * L'identifiant n'est pas attribué ici (voir etudiant_nouvel_id). */
int  etudiant_remplir(Etudiant *e, const char *nom, const char *prenom,
                      int age, char sexe, const float notes[NB_MATIERES]);
const char *etudiant_message_erreur(int code);

/* Matricules : compteur global croissant. */
int  etudiant_nouvel_id(void);
void etudiant_raz_ids(void);

/* Génération aléatoire avec rand() (exigence du sujet). */
void etudiant_aleatoire(Etudiant *e);
/* Étudiant aléatoire dont la moyenne vaut exactement cle/100 (jeux de données
 * contrôlés pour les meilleurs / pires cas). */
void etudiant_aleatoire_avec_cle(Etudiant *e, int cle);

/* Ordre total : par clé puis par matricule (utilisé par les tris et le tas). */
int  comparer_etudiants(const Etudiant *a, const Etudiant *b);

void etudiant_afficher_entete(FILE *f);
void etudiant_afficher(FILE *f, const Etudiant *e);

#endif
