@echo off

REM Ustawienie zmiennych
set REPO_URL=https://github.com/kampaniawrzesniowa1939/bzura1939rozpoczeta14042025.git
set BRANCH=main

REM Przejście do folderu projektu
cd /d %~dp0

REM Inicjalizacja repozytorium Git
git init

REM Dodanie zdalnego repozytorium
git remote add origin %REPO_URL%

REM Dodanie wszystkich plików do repozytorium
git add .

REM Utworzenie commita
git commit -m "Eksport projektu"

REM Ustawienie głównej gałęzi
git branch -M %BRANCH%

REM Wypchnięcie zmian na GitHuba
git push -u origin %BRANCH%

pause