# Genere automatiquement par benchmark.c — Bonus 2 - Recherche : ABR degenere vs ABR equilibre
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/bonus_abr_recherche.png'
set datafile separator ','
set datafile columnheaders
set title "Bonus 2 - Recherche : ABR degenere vs ABR equilibre" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.003460708261 * x
f1(x) = 0.001225684512 * log(x)/log(2)
plot 'resultats/recherche.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "ABR classique degenere", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "ABR equilibre", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(log n)"
unset output
