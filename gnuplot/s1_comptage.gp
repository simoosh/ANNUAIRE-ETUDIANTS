# Genere automatiquement par benchmark.c — S1 - Nombre d'etudiants ayant une moyenne donnee
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s1_comptage.png'
set datafile separator ','
set datafile columnheaders
set title "S1 - Nombre d'etudiants ayant une moyenne donnee" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.001546106693 * x
f1(x) = 0.00664306185 * x
plot 'resultats/comptage.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Tableau", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/comptage.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Liste chainee", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)"
unset output
