@echo off
rem ======================================================================
rem  build.bat - Compilation sans make (Windows + gcc MSYS2/MinGW)
rem    build.bat          compile CLI, bibliotheque de l'interface et tests
rem    build.bat test     compile puis execute les tests
rem ======================================================================
setlocal
cd /d "%~dp0"
where gcc >nul 2>nul || set "PATH=C:\msys64\ucrt64\bin;%PATH%"
if not exist build mkdir build
if not exist resultats mkdir resultats
if not exist graphiques mkdir graphiques
if not exist gnuplot mkdir gnuplot

set COMMUN=src\etudiant.c src\memoire.c src\instrument.c src\tris.c src\tas.c src\s1_tableau.c src\s1_liste.c src\s2_trie.c src\s3_abr.c src\annuaire.c src\benchmark.c
set CFLAGS=-std=c11 -O2 -Wall -Wextra

echo [1/3] Programme en ligne de commande (sans instrumentation, -O2)
gcc %CFLAGS% -DSANS_INSTRUMENTATION "-DOPTIONS_COMPILATION=\"gcc %CFLAGS% -DSANS_INSTRUMENTATION\"" -Wl,--stack,16777216 -o build\annuaire.exe %COMMUN% src\main.c -lm || goto erreur

echo [2/3] Bibliotheque de l'interface graphique (avec trace)
gcc %CFLAGS% -shared -static-libgcc -o build\annuaire.dll %COMMUN% src\api.c -lm || goto erreur

echo [3/3] Tests (suivi memoire)
gcc -std=c11 -O1 -g -Wall -Wextra -DSUIVI_MEMOIRE -o build\tests.exe tests\test_structures.c %COMMUN% -lm || goto erreur

echo Compilation terminee.
if /i "%1"=="test" build\tests.exe
exit /b 0

:erreur
echo ECHEC de la compilation.
exit /b 1
