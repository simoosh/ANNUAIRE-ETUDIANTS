# Genere automatiquement par benchmark.c — Comparaison - Ajout (cas moyen, ordre aleatoire)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/cmp_insertion.png'
set datafile separator ','
set datafile columnheaders
set title "Comparaison - Ajout (cas moyen, ordre aleatoire)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.02564313208 * 1
f1(x) = 0.04617564675 * 1
f2(x) = 0.0009772060474 * x
f3(x) = 0.02324132876 * log(x)/log(2)
plot 'resultats/insertion.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S1 tableau", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/insertion.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "S1 liste chainee", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(1)", \
     'resultats/insertion.csv' using 1:8 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "S2 tableau trie", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)", \
     'resultats/insertion.csv' using 1:11 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "S3 ABR", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(log n)"
unset output
