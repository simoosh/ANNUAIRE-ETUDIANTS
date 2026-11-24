# Genere automatiquement par benchmark.c — S3 - Hauteur de l'ABR selon l'ordre d'insertion
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s3_hauteur.png'
set datafile separator ','
set datafile columnheaders
set title "S3 - Hauteur de l'ABR selon l'ordre d'insertion" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Hauteur (niveaux)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 1 * x
f2(x) = 3.085376105 * log(x)/log(2)
plot 'resultats/hauteur.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Insertion croissante", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n)", \
     'resultats/hauteur.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Insertion decroissante", \
     'resultats/hauteur.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Insertion aleatoire", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(log n)", \
     'resultats/hauteur.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "Construction equilibree (bonus 2)", \
     'resultats/hauteur.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#9467bd' title "log2(n)"
unset output
