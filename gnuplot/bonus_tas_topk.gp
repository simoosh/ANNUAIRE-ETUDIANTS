# Genere automatiquement par benchmark.c — Bonus 1 - Top-k (k = 10) : tas max vs les trois structures
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/bonus_tas_topk.png'
set datafile separator ','
set datafile columnheaders
set title "Bonus 1 - Top-k (k = 10) : tas max vs les trois structures" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.01398415058 * x*log(x)/log(2)
f1(x) = 0.05274498378 * x
f2(x) = 0.00568064012 * log(x)/log(2)
f3(x) = 0.03213353483 * 1
plot 'resultats/topk.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "S1 : tri rapide + k derniers", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n log n)", \
     'resultats/topk.csv' using 1:10 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Tas max : ConstruireTasMax + k extractions", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/topk.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "S3 : infixe inverse", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(log n)", \
     'resultats/topk.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "S2 : lecture directe", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(1)"
unset output
