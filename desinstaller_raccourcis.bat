@echo off
chcp 65001 >nul
title Desinstallation - Comparateur Pro
color 0C

echo =======================================================
echo   Desinstallation des raccourcis - Comparateur Pro
echo =======================================================
echo.
echo Ce script retire le menu clic droit "Comparateur Pro".
echo Les fichiers du logiciel ne sont PAS supprimes.
echo.
echo Veuillez choisir la langue / Choose language :
echo [1] Francais
echo [2] English
set /p lang="Choix / Choice (1 ou 2) : "

if "%lang%"=="1" (
    set "MSG_WORK=Suppression des entrees du registre..."
    set "MSG_DONE=Desinstallation terminee. Le menu clic droit a ete retire."
) else (
    set "MSG_WORK=Removing registry entries..."
    set "MSG_DONE=Uninstall complete. The right-click menu has been removed."
)

echo.
echo %MSG_WORK%

:: Suppression des menus actuels (Comparateur Pro)
reg delete "HKCU\Software\Classes\SystemFileAssociations\image\shell\ComparateurPro" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\ComparateurPro" /f >nul 2>&1

:: Suppression d'eventuels anciens menus (versions anterieures)
reg delete "HKCU\Software\Classes\SystemFileAssociations\image\shell\Comparateur" /f >nul 2>&1
reg delete "HKCU\Software\Classes\Directory\shell\Comparateur" /f >nul 2>&1

echo.
echo %MSG_DONE%
pause
