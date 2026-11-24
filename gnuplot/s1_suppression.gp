# Genere automatiquement par benchmark.c — S1 - Suppression : tableau (decalages) vs liste chainee
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s1_suppression.png'
set datafile separator ','
set datafile columnheaders
set title "S1 - Suppression : tableau (decalages) vs liste chainee" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.003628622279 * x
f1(x) = 0.002473073323 * x
f2(x) = 0.001367031972 * x
f3(x) = 0.02406572405 * 1
f4(x) = 0.002693350336 * x
f5(x) = 0.006130821452 * x
plot 'resultats/suppression.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Tableau - 1er arrive (n-1 decalages)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/suppression.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Tableau - au hasard", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/suppression.csv' using 1:9 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Tableau - dernier arrive (n comparaisons)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)", \
     'resultats/suppression.csv' using 1:8 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "Liste - 1er arrive (meilleur cas)", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(1)", \
     'resultats/suppression.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#9467bd' title "Liste - au hasard", \
     f4(x) with lines dt 2 lw 1.5 lc rgb '#9467bd' title "  theorie Θ(n)", \
     'resultats/suppression.csv' using 1:10 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#8c564b' title "Liste - dernier arrive (pire cas)", \
     f5(x) with lines dt 2 lw 1.5 lc rgb '#8c564b' title "  theorie Θ(n)"
unset output
