@echo off
cd /d "%~dp0.."
powershell -ExecutionPolicy Bypass -File "%~dp0import-products.ps1" -SourceFile ".\products.csv" -ImageRoot ".\product-images" -DestinationRoot ".\public_html\user\pages\02.all_produts" -Force
