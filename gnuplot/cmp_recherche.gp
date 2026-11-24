# Genere automatiquement par benchmark.c — Comparaison - Recherche par moyenne (cas moyen)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/cmp_recherche.png'
set datafile separator ','
set datafile columnheaders
set title "Comparaison - Recherche par moyenne (cas moyen)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 7.466008656e-05 * x
f1(x) = 0.0002950556832 * x
f2(x) = 0.001364851302 * log(x)/log(2)
f3(x) = 0.001753201417 * log(x)/log(2)
plot 'resultats/recherche.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S1 tableau", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "S1 liste chainee", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "S2 tableau trie", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(log n)", \
     'resultats/recherche.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "S3 ABR", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(log n)"
unset output
