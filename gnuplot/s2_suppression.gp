# Genere automatiquement par benchmark.c — S2 - Suppression (dichotomie + decalages a gauche)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s2_suppression.png'
set datafile separator ','
set datafile columnheaders
set title "S2 - Suppression (dichotomie + decalages a gauche)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.002670495376 * log(x)/log(2)
f1(x) = 0.00170861733 * x
f2(x) = 0.003444005146 * x
plot 'resultats/suppression.csv' using 1:11 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Meilleur cas : plus grande moyenne (0 decalage)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(log n)", \
     'resultats/suppression.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Cas moyen : au hasard", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/suppression.csv' using 1:13 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Pire cas : plus petite moyenne (n decalages)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)"
unset output
