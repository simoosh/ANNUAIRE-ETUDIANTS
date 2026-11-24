/*
 * etudiant.c — Implémentation des opérations sur le type Etudiant.
 */
#include "etudiant.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

const char *NOMS_MATIERES[NB_MATIERES] = {
    "Algorithmique", "Analyse", "Algebre", "Architecture", "Anglais"
};

static const char *NOMS[] = {
    "Benali", "Haddad", "Mansouri", "Khelifi", "Amrani", "Saadi", "Belkacem",
    "Cherif", "Hamidi", "Meziane", "Ait Ahmed", "Bouzid", "Djebbar", "Ferhat",
    "Ghanem", "Hadj", "Ikhlef", "Kaci", "Larbi", "Madani", "Nait Ali", "Ouali",
    "Rahmani", "Slimani", "Tahar", "Yahiaoui", "Zerrouki", "Boukhalfa", "Medjber",
    "Amirouche", "Sahraoui", "Bensaid"
};
static const char *PRENOMS_M[] = {
    "Amine", "Yacine", "Karim", "Sofiane", "Walid", "Mehdi", "Lyes", "Rayan",
    "Idir", "Massinissa", "Anis", "Bilal", "Nassim", "Samir", "Hocine", "Aghiles",
    "Juba", "Farid", "Omar", "Riad"
};
static const char *PRENOMS_F[] = {
    "Amel", "Lina", "Sarah", "Yasmine", "Meriem", "Nesrine", "Kahina", "Lydia",
    "Thiziri", "Imane", "Rania", "Celia", "Feriel", "Dihia", "Asma", "Nour",
    "Tinhinane", "Ines", "Selma", "Melissa"
};
#define NB(t) ((int)(sizeof(t) / sizeof((t)[0])))

static int g_prochain_id = 1;

int etudiant_nouvel_id(void) { return g_prochain_id++; }
void etudiant_raz_ids(void)  { g_prochain_id = 1; }

int cle_depuis_moyenne(double moyenne)
{
    if (moyenne < 0.0 || moyenne > 20.0) return -1;
    return (int)floor(moyenne * 100.0 + 0.5);
}

void etudiant_calculer_moyenne(Etudiant *e)
{
    double somme = 0.0;
    int i;
    for (i = 0; i < NB_MATIERES; i++) somme += e->notes[i];
    /* arrondi au centième, calculé en entier pour être exact */
    e->cle = (int)floor(somme * 100.0 / NB_MATIERES + 0.5);
    if (e->cle > CLE_MAX) e->cle = CLE_MAX;
    if (e->cle < 0) e->cle = 0;
    e->moyenne = (float)(e->cle / 100.0);
}

/* Un nom valide : non vide, < TAILLE_NOM octets, lettres (ASCII ou UTF-8),
 * espaces, tirets et apostrophes ; au moins une lettre. */
static int nom_valide(const char *s)
{
    size_t n, i;
    int lettre = 0;
    if (!s) return 0;
    n = strlen(s);
    if (n == 0 || n >= TAILLE_NOM) return 0;
    for (i = 0; i < n; i++) {
        unsigned char c = (unsigned char)s[i];
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c >= 0x80) lettre = 1;
        else if (c != ' ' && c != '-' && c != '\'') return 0;
    }
    return lettre;
}

int etudiant_remplir(Etudiant *e, const char *nom, const char *prenom,
                     int age, char sexe, const float notes[NB_MATIERES])
{
    int i;
    if (!nom_valide(nom)) return ETU_ERR_NOM;
    if (!nom_valide(prenom)) return ETU_ERR_PRENOM;
    if (age < AGE_MIN || age > AGE_MAX) return ETU_ERR_AGE;
    if (sexe == 'm') sexe = 'M';
    if (sexe == 'f') sexe = 'F';
    if (sexe != 'M' && sexe != 'F') return ETU_ERR_SEXE;
    for (i = 0; i < NB_MATIERES; i++)
        if (!(notes[i] >= 0.0f && notes[i] <= 20.0f)) return ETU_ERR_NOTE;  /* rejette aussi NaN */

    memset(e, 0, sizeof *e);
    strncpy(e->nom, nom, TAILLE_NOM - 1);
    strncpy(e->prenom, prenom, TAILLE_NOM - 1);
    e->age = age;
    e->sexe = sexe;
    for (i = 0; i < NB_MATIERES; i++)  /* notes au centième */
        e->notes[i] = (float)(floor(notes[i] * 100.0 + 0.5) / 100.0);
    etudiant_calculer_moyenne(e);
    return ETU_OK;
}

const char *etudiant_message_erreur(int code)
{
    switch (code) {
    case ETU_OK:         return "OK";
    case ETU_ERR_NOM:    return "Nom invalide (1 a 31 caracteres : lettres, espace, - ou ')";
    case ETU_ERR_PRENOM: return "Prenom invalide (1 a 31 caracteres : lettres, espace, - ou ')";
    case ETU_ERR_AGE:    return "Age invalide (entre 16 et 80 ans)";
    case ETU_ERR_SEXE:   return "Sexe invalide (M ou F)";
    case ETU_ERR_NOTE:   return "Note invalide (entre 0 et 20)";
    default:             return "Erreur inconnue";
    }
}

static void identite_aleatoire(Etudiant *e)
{
    memset(e, 0, sizeof *e);
    e->sexe = (rand() % 2) ? 'M' : 'F';
    strncpy(e->nom, NOMS[rand() % NB(NOMS)], TAILLE_NOM - 1);
    if (e->sexe == 'M') strncpy(e->prenom, PRENOMS_M[rand() % NB(PRENOMS_M)], TAILLE_NOM - 1);
    else                strncpy(e->prenom, PRENOMS_F[rand() % NB(PRENOMS_F)], TAILLE_NOM - 1);
    e->age = 18 + rand() % 10;
    e->id = etudiant_nouvel_id();
}

void etudiant_aleatoire(Etudiant *e)
{
    int i;
    identite_aleatoire(e);
    for (i = 0; i < NB_MATIERES; i++)
        e->notes[i] = (float)((rand() % 2001) / 100.0);   /* 0.00 .. 20.00 */
    etudiant_calculer_moyenne(e);
}

void etudiant_aleatoire_avec_cle(Etudiant *e, int cle)
{
    int i, base[NB_MATIERES], d;
    identite_aleatoire(e);
    if (cle < 0) cle = 0;
    if (cle > CLE_MAX) cle = CLE_MAX;
    /* 5 notes (en centièmes) dont la somme vaut exactement 5*cle */
    for (i = 0; i < NB_MATIERES; i++) base[i] = cle;
    for (i = 0; i + 1 < NB_MATIERES; i += 2) {          /* perturbations +d / -d */
        int marge = cle < CLE_MAX - cle ? cle : CLE_MAX - cle;
        d = marge > 0 ? rand() % (marge + 1) : 0;
        if (d > 300) d = rand() % 301;                  /* écarts réalistes (<= 3 points) */
        base[i] += d;
        base[i + 1] -= d;
    }
    for (i = 0; i < NB_MATIERES; i++) e->notes[i] = (float)(base[i] / 100.0);
    etudiant_calculer_moyenne(e);
    e->cle = cle;                                       /* exact par construction */
    e->moyenne = (float)(cle / 100.0);
}

int comparer_etudiants(const Etudiant *a, const Etudiant *b)
{
    if (a->cle != b->cle) return a->cle < b->cle ? -1 : 1;
    if (a->id != b->id)   return a->id < b->id ? -1 : 1;
    return 0;
}

void etudiant_afficher_entete(FILE *f)
{
    fprintf(f, "%-6s %-14s %-12s %-4s %-4s %-29s %-7s\n",
            "Matr.", "Nom", "Prenom", "Age", "Sexe", "Notes (5 matieres)", "Moyenne");
}

void etudiant_afficher(FILE *f, const Etudiant *e)
{
    fprintf(f, "%-6d %-14s %-12s %-4d %-4c %5.2f %5.2f %5.2f %5.2f %5.2f  %6.2f\n",
            e->id, e->nom, e->prenom, e->age, e->sexe,
            e->notes[0], e->notes[1], e->notes[2], e->notes[3], e->notes[4],
            e->cle / 100.0);
}
