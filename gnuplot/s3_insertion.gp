# Genere automatiquement par benchmark.c — S3 - Ajout dans l'ABR (temps moyen par insertion)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s3_insertion.png'
set datafile separator ','
set datafile columnheaders
set title "S3 - Ajout dans l'ABR (temps moyen par insertion)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.02324132876 * log(x)/log(2)
f1(x) = 0.009626827592 * log(x)/log(2)
f2(x) = 0.005364048403 * x
f3(x) = 0.004926781166 * x
plot 'resultats/insertion.csv' using 1:11 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Ordre aleatoire", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(log n)", \
     'resultats/insertion.csv' using 1:14 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Construction equilibree (bonus 2)", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(log n)", \
     'resultats/insertion.csv' using 1:12 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Ordre croissant (ABR degenere)", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)", \
     'resultats/insertion.csv' using 1:13 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "Ordre decroissant (ABR degenere)", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(n)"
unset output
