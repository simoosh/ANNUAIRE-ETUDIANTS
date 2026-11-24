# Genere automatiquement par benchmark.c — S3 - Affichage trie : parcours infixe
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s3_affichage_trie.png'
set datafile separator ','
set datafile columnheaders
set title "S3 - Affichage trie : parcours infixe" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps total (ms)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 1.81536889e-05 * x
f1(x) = 9.629425773e-06 * x
plot 'resultats/affichage_trie.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "ABR aleatoire", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/affichage_trie.csv' using 1:8 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "ABR degenere", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)"
unset output
