@echo off
setlocal
set SOURCE_DIR=%~dp0
set BACKUP_DIR=%USERPROFILE%\backups\kampania1939_v2_fixed
set DATETIME=%DATE:~6,4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%
set DATETIME=%DATETIME: =0%
mkdir "%BACKUP_DIR%" 2>nul
xcopy "%SOURCE_DIR%" "%BACKUP_DIR%\%DATETIME%" /E /I /Y
echo Backup utworzony w: %BACKUP_DIR%\%DATETIME%
pause
