# Genere automatiquement par benchmark.c — Bonus 1 - Top-k en fonction de k (n maximal)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/bonus_tas_topk_k.png'
set datafile separator ','
set datafile columnheaders
set title "Bonus 1 - Top-k en fonction de k (n maximal)" font 'Arial,14'
set xlabel "k (nombre de meilleurs etudiants)"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale x
set logscale y
plot 'resultats/topk_k.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S1 : tri rapide", \
     'resultats/topk_k.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Tas max", \
     'resultats/topk_k.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "S3 : infixe inverse", \
     'resultats/topk_k.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "S2 : lecture directe"
unset output
