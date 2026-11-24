# Genere automatiquement par benchmark.c — S1 - Recherche sequentielle (existence)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s1_recherche.png'
set datafile separator ','
set datafile columnheaders
set title "S1 - Recherche sequentielle (existence)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.004336072307 * 1
f1(x) = 7.466008656e-05 * x
f2(x) = 0.001509943991 * x
f4(x) = 0.0002950556832 * x
f5(x) = 0.006559527918 * x
plot 'resultats/recherche.csv' using 1:8 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Tableau - meilleur cas (1er element)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/recherche.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Tableau - cas moyen", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:12 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Tableau - pire cas (absente)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:9 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "Liste - meilleur cas", \
     'resultats/recherche.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#9467bd' title "Liste - cas moyen", \
     f4(x) with lines dt 2 lw 1.5 lc rgb '#9467bd' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:13 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#8c564b' title "Liste - pire cas (absente)", \
     f5(x) with lines dt 2 lw 1.5 lc rgb '#8c564b' title "  theorie Θ(n)"
unset output
