# Genere automatiquement par benchmark.c — S2 - Affichage trie : simple parcours
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s2_affichage_trie.png'
set datafile separator ','
set datafile columnheaders
set title "S2 - Affichage trie : simple parcours" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps total (ms)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 5.27780105e-06 * x
plot 'resultats/affichage_trie.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S2", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)"
unset output
