# Genere automatiquement par benchmark.c — S2 - Top-k (k = 10) : lecture directe des k derniers
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s2_topk.png'
set datafile separator ','
set datafile columnheaders
set title "S2 - Top-k (k = 10) : lecture directe des k derniers" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.03213353483 * 1
plot 'resultats/topk.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S2", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)"
unset output
