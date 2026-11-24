# Genere automatiquement par benchmark.c — S3 - Top-k (k = 10) : parcours infixe inverse arrete apres k
# Courbes pleines : mesures (clock()). Pointilles : complexite theorique a*f(n),
# a ajuste par moindres carres sur les mesures de la meme serie.
set encoding utf8
set terminal pngcairo size 1100,680 enhanced font 'Arial,11'
set output 'graphiques/s3_topk.png'
set datafile separator ','
set datafile columnheaders
set title "S3 - Top-k (k = 10) : parcours infixe inverse arrete apres k" font 'Arial,14'
set xlabel "Taille de la base n"
set ylabel "Temps moyen par operation (µs)"
set grid lc rgb '#dddddd'
set key left top box opaque font 'Arial,9'
set logscale y
f0(x) = 0.05777679716 * 1
f1(x) = 0.00568064012 * log(x)/log(2)
f2(x) = 0.005937874094 * log(x)/log(2)
f3(x) = 0.01490851931 * x
plot 'resultats/topk.csv' using 1:8 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#1f77b4' title "Degenere a gauche : max a la racine (meilleur)", \
     f0(x) with lines dt 2 lw 1.5 lc rgb '#1f77b4' title "  theorie Θ(1)", \
     'resultats/topk.csv' using 1:6 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#d62728' title "ABR aleatoire", \
     f1(x) with lines dt 2 lw 1.5 lc rgb '#d62728' title "  theorie Θ(log n)", \
     'resultats/topk.csv' using 1:9 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#2ca02c' title "ABR equilibre", \
     f2(x) with lines dt 2 lw 1.5 lc rgb '#2ca02c' title "  theorie Θ(log n)", \
     'resultats/topk.csv' using 1:7 with linespoints lw 2 pt 7 ps 0.8 lc rgb '#ff7f0e' title "Degenere a droite : max au fond (pire)", \
     f3(x) with lines dt 2 lw 1.5 lc rgb '#ff7f0e' title "  theorie Θ(n)"
unset output
