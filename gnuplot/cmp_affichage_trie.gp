# Genere automatiquement par benchmark.c — Comparaison - Affichage trie
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/cmp_affichage_trie.png'
set datafile separator ','
set datafile columnheaders
set title "Comparaison - Affichage trie" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps total (ms)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 1.290395317e-05 * x*log(x)/log(2)
f1(x) = 1.276089525e-05 * x*log(x)/log(2)
f2(x) = 5.27780105e-06 * x
f3(x) = 1.81536889e-05 * x
plot 'resultats/affichage_trie.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S1 tableau", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n log n)", \
     'resultats/affichage_trie.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "S1 liste chainee", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n log n)", \
     'resultats/affichage_trie.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "S2 tableau trie", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)", \
     'resultats/affichage_trie.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "S3 ABR", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(n)"
unset output
