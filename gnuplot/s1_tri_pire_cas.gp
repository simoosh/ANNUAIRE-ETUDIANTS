# Genere automatiquement par benchmark.c — S1 - Pire cas du tri rapide : pivot = dernier element sur donnees triees
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s1_tri_pire_cas.png'
set datafile separator ','
set datafile columnheaders
set title "S1 - Pire cas du tri rapide : pivot = dernier element sur donnees triees" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps total (ms)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 1.290395317e-05 * x*log(x)/log(2)
f1(x) = 4.582857057e-06 * x*log(x)/log(2)
f2(x) = 2.191408045e-06 * x**2
plot 'resultats/affichage_trie.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Pivot median de 3, aleatoire", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n log n)", \
     'resultats/affichage_trie.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Pivot median de 3, deja trie", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n log n)", \
     'resultats/affichage_trie.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Pivot dernier, deja trie (pire cas)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n²)"
unset output
