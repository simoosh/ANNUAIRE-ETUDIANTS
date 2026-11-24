# Déroulé de la soutenance (15 minutes)

Préparation : `build.bat`, puis lancer `python gui\main.py`. L'étude complète a déjà été exécutée (`resultats/` et `graphiques/` remplis). Garder un terminal ouvert pour montrer le menu C.

| Temps | Section | Ce qu'on montre | Message clé |
|---|---|---|---|
| 0:00 | Tableau de bord | 4 structures synchronisées, taille, mémoire, hauteur ABR | même contenu, même ordre d'arrivée → comparaison équitable |
| 1:00 | Gestion des étudiants | ajout avec une erreur volontaire (note 21) puis correct ; générer n = 1000 ; rechercher une moyenne (existence + nombre par structure) ; top-10 ; supprimer | validation des saisies, doublons gérés par matricule |
| 3:00 | S1 | « Base démo » ; recherche séquentielle animée ; suppression (décalages) ; basculer en liste chaînée (pas de décalage) ; top-k → animation du tri rapide sur la copie | effet tableau / liste chaînée |
| 4:30 | S2 | ajouter une petite moyenne (décalages) ; rechercher (dichotomie g/m/d) ; top-k direct | insertion Θ(n), recherche Θ(log n) |
| 6:00 | Visualiseur > ABR | « Arbre démo 3 cas » puis « Cas feuille », « Cas un fils », « Cas deux fils » | successeur = minimum du sous-arbre droit |
| 7:30 | Visualiseur | tri rapide (pivot, partition, échanges) ; tri par insertion | même code C que S1 / S2 |
| 8:30 | Tas max | animation ConstruireTasMax + extractions ; onglet comparaison | Θ(n + k log n) : 3× plus rapide que le tri complet pour k = 10 |
| 9:30 | ABR équilibré | construire les deux arbres (peigne vs équilibré) ; animer le milieu d'abord ; mesurer n = 5000 | hauteur n vs ⌈log2(n+1)⌉ |
| 10:30 | Étude expérimentale | protocole, journal, CSV, galerie gnuplot | clock(), répétitions, copies hors chrono, system() |
| 12:00 | Comparaison des complexités | tableaux de bord S1, S2, S3 ; comparaison ; tableau théorique et synthèse | pointillés = théorie ajustée ; doublons et cache expliquent les écarts |
| 13:30 | Conclusion | rapports et export | ajouts → S1 ; recherches / tri → S2 ; base dynamique → S3 |
| 14:30 | Questions | | |

## Questions probables

- **Pourquoi `cle` entière ?** Pour comparer exactement : `12.50 == 12.50` en `float` dépend de l'arrondi.
- **Pourquoi la recherche réussie dans S1 plafonne-t-elle ?** Doublons : la première occurrence d'une moyenne partagée par d étudiants est vers n/(d+1).
- **Pourquoi l'ABR aléatoire est-il plus haut que 2 ln n ?** Les étudiants de même moyenne arrivent par matricule croissant : insertions croissantes locales.
- **Pourquoi les opérations de l'ABR sont-elles itératives ?** Un peigne de 20 000 nœuds = 20 000 appels récursifs → débordement de pile.
- **Comment les suppressions sont-elles mesurées ?** Copie de la structure hors chronométrage, n/10 suppressions chronométrées, destruction hors chronométrage.
- **Les animations sont-elles réelles ?** Oui : les fonctions C émettent une trace (instrument.h) que l'interface rejoue ; le code mesuré est compilé sans cette trace.
