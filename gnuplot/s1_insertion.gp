# Genere automatiquement par benchmark.c — S1 - Ajout : temps moyen par insertion
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s1_insertion.png'
set datafile separator ','
set datafile columnheaders
set title "S1 - Ajout : temps moyen par insertion" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.02564313208 * 1
f3(x) = 0.04617564675 * 1
plot 'resultats/insertion.csv' using 1:2 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Tableau, ordre aleatoire", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/insertion.csv' using 1:3 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Tableau, ordre croissant", \
     'resultats/insertion.csv' using 1:4 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Tableau, ordre decroissant", \
     'resultats/insertion.csv' using 1:5 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "Liste chainee, ordre aleatoire", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(1)"
unset output
