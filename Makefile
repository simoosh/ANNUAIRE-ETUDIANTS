# Makefile — Mini-projet A : Gestionnaire d'annuaire d'étudiants
#
#   make            programme CLI + bibliothèque pour l'interface + tests
#   make test       tests de validation (fuites mémoire / hors bornes)
#   make bench      étude expérimentale complète (CSV + gnuplot)
#   make bench-rapide
#   make graphes    relance gnuplot sur les derniers résultats
#   make gui        lance l'interface graphique
#   make rapport    génère le rapport Word à partir des résultats
#   make clean
#
# Sous Windows (MSYS2) : utiliser « mingw32-make » ; sans make : build.bat

CC      = gcc
CFLAGS  = -std=c11 -O2 -Wall -Wextra
LDLIBS  = -lm
PYTHON  ?= python

COMMUN  = src/etudiant.c src/memoire.c src/instrument.c src/tris.c src/tas.c \
          src/s1_tableau.c src/s1_liste.c src/s2_trie.c src/s3_abr.c src/annuaire.c \
          src/benchmark.c
EN_TETES = $(wildcard src/*.h)

ifeq ($(OS),Windows_NT)
  EXE = .exe
  LIB = build/annuaire.dll
  PILE = -Wl,--stack,16777216
else
  EXE =
  LIB = build/libannuaire.so
  PILE =
  CFLAGS += -fPIC
endif

CLI   = build/annuaire$(EXE)
TESTS = build/tests$(EXE)

# Options figées dans resultats/protocole.txt
OPT_MESURE = -DSANS_INSTRUMENTATION
DEF_OPTS   = -DOPTIONS_COMPILATION="\"$(CC) $(CFLAGS) $(OPT_MESURE)\""

all: $(CLI) $(LIB) $(TESTS)

build:
	mkdir -p build resultats graphiques gnuplot

# Programme en ligne de commande et benchmark : SANS instrumentation
$(CLI): $(COMMUN) src/main.c $(EN_TETES) | build
	$(CC) $(CFLAGS) $(OPT_MESURE) $(DEF_OPTS) $(PILE) -o $@ $(COMMUN) src/main.c $(LDLIBS)

# Bibliothèque pour l'interface : AVEC trace et compteurs (animations)
$(LIB): $(COMMUN) src/api.c $(EN_TETES) | build
	$(CC) $(CFLAGS) -shared -static-libgcc -o $@ $(COMMUN) src/api.c $(LDLIBS)

# Tests : suivi des allocations et des débordements
$(TESTS): $(COMMUN) tests/test_structures.c $(EN_TETES) | build
	$(CC) -std=c11 -O1 -g -Wall -Wextra -DSUIVI_MEMOIRE -o $@ tests/test_structures.c $(COMMUN) $(LDLIBS)

test: $(TESTS)
	./$(TESTS)

bench: $(CLI)
	./$(CLI) --bench

bench-rapide: $(CLI)
	./$(CLI) --bench --rapide

graphes: $(CLI)
	./$(CLI) --gnuplot

gui: $(LIB)
	$(PYTHON) gui/main.py

rapport:
	$(PYTHON) rapport/generer_rapport.py

clean:
	rm -f build/*

.PHONY: all test bench bench-rapide graphes gui rapport clean
