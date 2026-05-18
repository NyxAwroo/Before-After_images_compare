@echo off
chcp 65001 >nul
title Installation - Comparateur Pro
color 0B

echo =======================================================
echo   Installation des raccourcis - Comparateur Pro
echo =======================================================
echo.
echo Ce script configure le clic droit automatiquement.
echo Dossier detecte : %~dp0
echo.

:: Récupération automatique du chemin actuel
set "APP_PATH=%~dp0comparateur_app.py"

:: --- VERIFICATION 1 : le fichier principal existe-t-il bien ici ? ---
if not exist "%APP_PATH%" (
    color 0C
    echo [ERREUR] comparateur_app.py est introuvable dans ce dossier.
    echo          comparateur_app.py was not found in this folder.
    echo.
    echo Placez ce .bat dans le meme dossier que comparateur_app.py,
    echo puis relancez-le. / Put this .bat next to comparateur_app.py.
    echo.
    pause
    exit /b 1
)

:: --- VERIFICATION 2 : la commande pyw est-elle disponible ? ---
where pyw >nul 2>&1
if errorlevel 1 (
    color 0E
    echo [ATTENTION] La commande "pyw" est introuvable dans le PATH.
    echo             "pyw" was not found in your PATH.
    echo.
    echo Le menu sera installe, mais le logiciel ne se lancera pas tant
    echo que Python ne sera pas correctement installe et ajoute au PATH.
    echo The menu will be installed, but the app will not start until
    echo Python is properly installed and added to PATH.
    echo.
    echo Conseil : reinstallez Python en cochant "Add Python to PATH".
    echo.
    pause
)

echo Veuillez choisir la langue du menu / Choose menu language :
echo [1] Francais
echo [2] English
set /p lang="Choix / Choice (1 ou 2) : "

if "%lang%"=="1" (
    set "NAME=Comparateur Pro"
    set "TXT_OPEN=1. Ouvrir dans Comparateur Pro"
    set "TXT_EXP=2. Generer Export Rapide"
    set "TXT_DIR_OPEN=1. Ouvrir le dossier dans Comparateur Pro"
    set "TXT_DIR_EXP=2. Export Batch (Tout le dossier)"
    set "MSG_SUCCESS=Installation terminee avec succes ! Vous pouvez faire un clic droit sur vos images."
) else (
    set "NAME=Pro Comparator"
    set "TXT_OPEN=1. Open in Pro Comparator"
    set "TXT_EXP=2. Generate Quick Export"
    set "TXT_DIR_OPEN=1. Open folder in Pro Comparator"
    set "TXT_DIR_EXP=2. Batch Export (Whole folder)"
    set "MSG_SUCCESS=Installation completed successfully! You can now right-click your images."
)

echo.
echo Nettoyage des anciens menus...
reg delete "HKCU\Software\Classes\SystemFileAssociations\image\shell\Comparateur" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\Comparateur" /f >nul 2>&1
reg delete "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\ComparateurPro" /f >nul 2>&1

echo Creation des menus pour les images...
reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro" /v "MUIVerb" /t REG_SZ /d "%NAME%" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro" /v "Icon" /t REG_SZ /d "imageres.dll,-68" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro" /v "SubCommands" /t REG_SZ /d "" /f >nul

reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro\shell\cmd1" /v "MUIVerb" /t REG_SZ /d "%TXT_OPEN%" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro\shell\cmd1\command" /ve /t REG_SZ /d "pyw \"%APP_PATH%\" \"%%1\"" /f >nul

reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro\shell\cmd2" /v "MUIVerb" /t REG_SZ /d "%TXT_EXP%" /f >nul
reg add "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro\shell\cmd2\command" /ve /t REG_SZ /d "pyw \"%APP_PATH%\" \"%%1\" --export-rapide" /f >nul

echo Creation des menus pour les dossiers...
reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro" /v "MUIVerb" /t REG_SZ /d "%NAME%" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro" /v "Icon" /t REG_SZ /d "imageres.dll,-68" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro" /v "SubCommands" /t REG_SZ /d "" /f >nul

reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro\shell\cmd1" /v "MUIVerb" /t REG_SZ /d "%TXT_DIR_OPEN%" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro\shell\cmd1\command" /ve /t REG_SZ /d "pyw \"%APP_PATH%\" \"%%V\"" /f >nul

reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro\shell\cmd2" /v "MUIVerb" /t REG_SZ /d "%TXT_DIR_EXP%" /f >nul
reg add "HKCU\Software\Classes\Directory\shell\ComparateurPro\shell\cmd2\command" /ve /t REG_SZ /d "pyw \"%APP_PATH%\" \"%%V\" --batch" /f >nul

echo.
echo %MSG_SUCCESS%
pause
