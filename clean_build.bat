@echo off
setlocal
set ROOT=%~dp0

echo Cleaning build artifacts in %ROOT%
echo.

if exist "%ROOT%build" (
    echo Removing build\
    rmdir /s /q "%ROOT%build"
)
if exist "%ROOT%build_temp" (
    echo Removing build_temp\
    rmdir /s /q "%ROOT%build_temp"
)
if exist "%ROOT%build_data" (
    echo Removing build_data\
    rmdir /s /q "%ROOT%build_data"
)
if exist "%ROOT%dist" (
    echo Removing dist\
    rmdir /s /q "%ROOT%dist"
)

echo.
echo Done. This frees ~500 MB - 1 GB+ depending on previous builds.
echo Your source Tesseract folder and .build-venv are kept.
echo.
echo Also free Windows temp on C: if builds still fail:
echo   Press Win+R, type %%TEMP%%, delete old files
echo.
endlocal
