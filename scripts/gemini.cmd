@echo off
REM Windows batch wrapper for Gemini CLI
REM This wrapper ensures proper execution on Windows systems

setlocal enabledelayedexpansion

REM Try to find gemini executable in various locations
set GEMINI_EXE=
set SEARCH_PATHS=%GEMINI_CLI_PATH%;%PATH%;%APPDATA%\npm;%LOCALAPPDATA%\Programs\claif\bin;%USERPROFILE%\.local\bin

REM Check GEMINI_CLI_PATH first
if defined GEMINI_CLI_PATH (
    if exist "%GEMINI_CLI_PATH%\gemini.cmd" (
        set GEMINI_EXE=%GEMINI_CLI_PATH%\gemini.cmd
    ) else if exist "%GEMINI_CLI_PATH%\gemini.exe" (
        set GEMINI_EXE=%GEMINI_CLI_PATH%\gemini.exe
    ) else if exist "%GEMINI_CLI_PATH%" (
        set GEMINI_EXE=%GEMINI_CLI_PATH%
    )
)

REM Search in PATH if not found
if not defined GEMINI_EXE (
    for %%i in (gemini.cmd gemini.exe gemini.bat gemini) do (
        set RESULT=
        for %%j in ("%%~$PATH:i") do set RESULT=%%~j
        if defined RESULT (
            set GEMINI_EXE=!RESULT!
            goto :found
        )
    )
)

REM Check npm global installation
if not defined GEMINI_EXE (
    if exist "%APPDATA%\npm\gemini.cmd" (
        set GEMINI_EXE=%APPDATA%\npm\gemini.cmd
    ) else if exist "%APPDATA%\npm\gemini.exe" (
        set GEMINI_EXE=%APPDATA%\npm\gemini.exe
    )
)

REM Check Claif installation directory
if not defined GEMINI_EXE (
    if exist "%LOCALAPPDATA%\Programs\claif\bin\gemini.cmd" (
        set GEMINI_EXE=%LOCALAPPDATA%\Programs\claif\bin\gemini.cmd
    ) else if exist "%LOCALAPPDATA%\Programs\claif\bin\gemini.exe" (
        set GEMINI_EXE=%LOCALAPPDATA%\Programs\claif\bin\gemini.exe
    )
)

:found
if not defined GEMINI_EXE (
    echo Error: Gemini CLI not found.
    echo.
    echo Please install Gemini CLI using one of these methods:
    echo   npm install -g @google/gemini-cli
    echo   bun add -g @google/gemini-cli
    echo   claif install gemini
    echo.
    echo Or set GEMINI_CLI_PATH environment variable to the installation directory.
    exit /b 1
)

REM Execute Gemini with all arguments
"%GEMINI_EXE%" %*
exit /b %ERRORLEVEL%