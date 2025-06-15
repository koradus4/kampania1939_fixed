@echo off
echo ============================================
echo BACKUP LOKALNY - KAMPANIA 1939 (PORZADKOWANIE)
echo ============================================

set timestamp=%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set timestamp=%timestamp: =0%

set source=C:\Users\klif\kampania1939_fixed
set backup_dir=C:\Users\klif\Backups\kampania1939_backup_%timestamp%

echo Tworze backup lokalny...
echo Źródło: %source%
echo Cel: %backup_dir%

if not exist "C:\Users\klif\Backups" mkdir "C:\Users\klif\Backups"

echo Kopiuje pliki...
xcopy "%source%" "%backup_dir%" /E /I /H /Y

echo.
echo ✅ BACKUP LOKALNY GOTOWY!
echo Lokalizacja: %backup_dir%
echo.
echo ZAWARTOŚĆ:
dir "%backup_dir%" /b

echo.
echo ============================================
echo BACKUP ZAKOŃCZONY POMYŚLNIE
echo ============================================
pause
