@echo off
setlocal
cd /d "%~dp0.."

set "DEFAULT_DEST=public_html\user\pages\02.all_produts"

echo Product Import
set /p SOURCE_FILE=Source CSV or Excel file path: 
if "%SOURCE_FILE%"=="" goto :usage

set /p IMAGE_ROOT=Image folder path: 
if "%IMAGE_ROOT%"=="" goto :usage

set /p DRY_RUN=Dry run first? (Y/N, default Y): 
if /I "%DRY_RUN%"=="N" (
    powershell -ExecutionPolicy Bypass -File "%~dp0import-products.ps1" -SourceFile "%SOURCE_FILE%" -ImageRoot "%IMAGE_ROOT%" -DestinationRoot "%DEFAULT_DEST%" -Force
) else (
    powershell -ExecutionPolicy Bypass -File "%~dp0import-products.ps1" -SourceFile "%SOURCE_FILE%" -ImageRoot "%IMAGE_ROOT%" -DestinationRoot "%DEFAULT_DEST%" -DryRun
)

echo.
pause
goto :eof

:usage
echo.
echo Source file path and image folder path are required.
echo.
pause
