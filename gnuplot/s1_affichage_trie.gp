# Genere automatiquement par benchmark.c — S1 - Affichage trie : copie + tri rapide
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s1_affichage_trie.png'
set datafile separator ','
set datafile columnheaders
set title "S1 - Affichage trie : copie + tri rapide" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps total (ms)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 1.290395317e-05 * x*log(x)/log(2)
f2(x) = 1.276089525e-05 * x*log(x)/log(2)
plot 'resultats/affichage_trie.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Tableau, donnees aleatoires", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n log n)", \
     'resultats/affichage_trie.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Tableau, donnees deja triees (pivot median de 3)", \
     'resultats/affichage_trie.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Liste chainee, donnees aleatoires", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n log n)"
unset output
