@echo off
setlocal

set ROOT=%~dp0
set PY=%ROOT%.build-venv\Scripts\python.exe
set FLET=%ROOT%.build-venv\Scripts\flet.exe

rem Build uses lots of temp space. Keep temp on the project drive (not full C:).
set TEMP=%ROOT%build_temp
set TMP=%TEMP%
if not exist "%TEMP%" mkdir "%TEMP%"

echo Build temp folder: %TEMP%
echo.

rem Free disk space from previous failed/partial builds
if exist "%ROOT%build" (
    echo Cleaning old build folder...
    rmdir /s /q "%ROOT%build" 2>nul
)
if exist "%TEMP%" (
    echo Cleaning build temp folder...
    rmdir /s /q "%TEMP%" 2>nul
    mkdir "%TEMP%"
)

if not exist "%PY%" (
    echo Creating build virtual environment...
    python -m venv "%ROOT%.build-venv"
)

echo Installing build dependencies into venv...
"%PY%" -m pip install --no-cache-dir -r requirements.txt pyinstaller
if errorlevel 1 (
    echo.
    echo pip install failed. If you see "No space left on device", free disk space first.
    echo Try: clean_build.bat  then run build again.
    exit /b 1
)

echo.
echo Preparing slim release bundle (smaller exe)...
if "%LITE%"=="1" (
    echo Lite mode: smaller English OCR model
    "%PY%" prepare_release.py --lite
) else (
    "%PY%" prepare_release.py
)
if errorlevel 1 exit /b 1

echo.
echo Building PersianOCR.exe (this may take 5-15 minutes)...
echo Need ~2 GB free on this drive during build.
"%FLET%" pack main.py ^
  --name PersianOCR ^
  --icon assets\icon.ico ^
  --add-data "build_data\Tesseract;Tesseract" ^
  --add-data "build_data\assets;assets" ^
  --product-name "Persian OCR" ^
  --product-version 1.5.0 ^
  --file-description "Persian OCR Desktop App by Hamed Gharghi" ^
  --company-name "Hamed Gharghi" ^
  --hidden-import fitz ^
  --hidden-import cv2 ^
  --hidden-import numpy ^
  --hidden-import ocr_utils ^
  --hidden-import export_utils ^
  --hidden-import settings ^
  --hidden-import tessdata_manager ^
  --hidden-import docx ^
  --hidden-import windnd ^
  --hidden-import PIL ^
  -y

if exist "dist\PersianOCR.exe" (
    echo.
    echo Build complete: dist\PersianOCR.exe
    for %%A in ("dist\PersianOCR.exe") do echo Size: %%~zA bytes
    echo Share this file with users - no Python install needed.
    rmdir /s /q "%TEMP%" 2>nul
) else (
    echo.
    echo Build failed. Check the output above.
    echo If disk was full, run clean_build.bat and free space on C: and D:.
    exit /b 1
)

endlocal
