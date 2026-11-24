# Genere automatiquement par benchmark.c — S3 - Comptage (parcours elague)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s3_comptage.png'
set datafile separator ','
set datafile columnheaders
set title "S3 - Comptage (parcours elague)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.07232742287 * log(x)/log(2)
f1(x) = 0.04371378534 * log(x)/log(2)
f2(x) = 0.01306898589 * x
plot 'resultats/comptage.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "ABR aleatoire", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(log n)", \
     'resultats/comptage.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "ABR equilibre", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(log n)", \
     'resultats/comptage.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "ABR degenere", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)"
unset output
