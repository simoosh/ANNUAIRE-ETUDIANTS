# Genere automatiquement par benchmark.c — S3 - Recherche dans l'ABR
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s3_recherche.png'
set datafile separator ','
set datafile columnheaders
set title "S3 - Recherche dans l'ABR" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.004499257824 * 1
f1(x) = 0.001753201417 * log(x)/log(2)
f2(x) = 0.001119694784 * log(x)/log(2)
f3(x) = 0.001225684512 * log(x)/log(2)
f4(x) = 0.003460708261 * x
f5(x) = 0.007668409667 * x
plot 'resultats/recherche.csv' using 1:11 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Meilleur cas (racine)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/recherche.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "ABR aleatoire - moyenne existante", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(log n)", \
     'resultats/recherche.csv' using 1:15 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "ABR aleatoire - absente > max (branche droite)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(log n)", \
     'resultats/recherche.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "ABR equilibre - moyenne existante", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(log n)", \
     'resultats/recherche.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#9467bd' title "ABR degenere - moyenne existante", \
     f4(x) with lines dt 2 lw 1.5 lc rgb '#9467bd' title "  theorie Θ(n)", \
     'resultats/recherche.csv' using 1:16 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#8c564b' title "ABR degenere - moyenne absente", \
     f5(x) with lines dt 2 lw 1.5 lc rgb '#8c564b' title "  theorie Θ(n)"
unset output
