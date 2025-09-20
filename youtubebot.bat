@echo off
echo ===============================================
echo         YouTube Watcher - Docker Windows
echo ===============================================
echo.

if "%1"=="" (
    echo Usage:
    echo   youtubebot.bat [headless^|gui] [URL] [duration] [loops]
    echo.
    echo Examples:
    echo   youtubebot.bat headless "https://www.youtube.com/watch?v=dQw4w9WgXcQ" "00:02:00" 3
    echo   youtubebot.bat gui
    echo.
    echo Starting in headless mode with default settings...
    docker run --rm youtubebot-main-youtubebot:latest /app/start.sh headless --url "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --duration "00:01:00" --loops 1
    goto :eof
)

if "%1"=="gui" (
    echo Starting with GUI...
    docker-compose up
    goto :eof
)

if "%1"=="headless" (
    if "%2"=="" (
        echo YouTube URL required!
        goto :eof
    )
    if "%3"=="" (
        echo Duration in HH:MM:SS format required!
        goto :eof
    )
    if "%4"=="" (
        echo Number of loops required!
        goto :eof
    )
    
    echo Starting headless with parameters...
    echo URL: %2
    echo Duration: %3
    echo Loops: %4
    echo.
    docker run --rm youtubebot-main-youtubebot:latest /app/start.sh headless --url %2 --duration %3 --loops %4
    goto :eof
)

echo Unknown option: %1
echo Available options: headless, gui