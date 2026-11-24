# Genere automatiquement par benchmark.c — S2 - Ajout avec maintien de l'ordre (principe du tri par insertion)
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s2_insertion.png'
set datafile separator ','
set datafile columnheaders
set title "S2 - Ajout avec maintien de l'ordre (principe du tri par insertion)" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
f0(x) = 0.03059564257 * 1
f1(x) = 0.0009772060474 * x
f2(x) = 0.001978852753 * x
plot 'resultats/insertion.csv' using 1:9 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Meilleur cas : arrivees croissantes (0 decalage)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/insertion.csv' using 1:8 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "Cas moyen : arrivees aleatoires", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n)", \
     'resultats/insertion.csv' using 1:10 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "Pire cas : arrivees decroissantes", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n)"
unset output
