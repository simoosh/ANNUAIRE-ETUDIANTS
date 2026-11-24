# Genere automatiquement par benchmark.c — Bonus 2 - Construction : ABR classique (moyennes croissantes) vs ABR equilibre
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/bonus_abr_construction.png'
set datafile separator ','
set datafile columnheaders
set title "Bonus 2 - Construction : ABR classique (moyennes croissantes) vs ABR equilibre" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps total (ms)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 5.393987933e-06 * x**2
f1(x) = 1.009442171e-05 * x*log(x)/log(2)
f2(x) = 2.880537678e-05 * x*log(x)/log(2)
plot 'resultats/construction.csv' using 1:12 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "ABR classique, insertions croissantes (pire cas)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(n²)", \
     'resultats/construction.csv' using 1:14 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "ABR equilibre (milieu d'abord)", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(n log n)", \
     'resultats/construction.csv' using 1:11 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "ABR classique, ordre aleatoire", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(n log n)"
unset output
