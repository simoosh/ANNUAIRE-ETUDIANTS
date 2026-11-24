# Genere automatiquement par benchmark.c — S2 - Comptage par deux dichotomies (bornes inf. et sup.)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s2_comptage.png'
set datafile separator ','
set datafile columnheaders
set title "S2 - Comptage par deux dichotomies (bornes inf. et sup.)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.003336359154 * log(x)/log(2)
plot 'resultats/comptage.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S2 tableau trie", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(log n)"
unset output
