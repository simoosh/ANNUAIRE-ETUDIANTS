# Genere automatiquement par benchmark.c — S2 - Recherche dichotomique et comptage
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s2_recherche.png'
set datafile separator ','
set datafile columnheaders
set title "S2 - Recherche dichotomique et comptage" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.0044780649 * 1
f1(x) = 0.001364851302 * log(x)/log(2)
f2(x) = 0.001956907638 * log(x)/log(2)
plot 'resultats/recherche.csv' using 1:10 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Meilleur cas (element du milieu)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/recherche.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Cas moyen (moyenne existante)", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(log n)", \
     'resultats/recherche.csv' using 1:14 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Pire cas (moyenne absente)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(log n)"
unset output
