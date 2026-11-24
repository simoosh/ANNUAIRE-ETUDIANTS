# Genere automatiquement par benchmark.c — Comparaison - Occupation memoire
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/cmp_memoire.png'
set datafile separator ','
set datafile columnheaders
set title "Comparaison - Occupation memoire" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Memoire (Ko)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.1494580505 * x
f1(x) = 0.1093766453 * x
f2(x) = 0.1494580505 * x
f3(x) = 0.1171885969 * x
plot 'resultats/memoire.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S1 tableau (capacite doublee)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/memoire.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "S1 liste chainee", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/memoire.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "S2 tableau trie", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)", \
     'resultats/memoire.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "S3 ABR", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(n)"
unset output
