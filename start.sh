#!/bin/bash
# Startup script for YouTube Bot in Docker

# Set X11 environment variables
export DISPLAY=:99
export XAUTHORITY=/tmp/.X99-lock

# Check if Xvfb is running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "Starting Xvfb..."
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset &
    XVFB_PID=$!
fi

# Create Xauthority file (to avoid PyAutoGUI errors)
touch $XAUTHORITY
chmod 600 $XAUTHORITY

# Check if window manager is running  
if ! pgrep -x "fluxbox" > /dev/null; then
    echo "Starting window manager..."
    fluxbox &
    WM_PID=$!
fi

# Wait for X11
echo "Waiting for X11 to be ready..."
sleep 5

# Check startup mode
if [ "$1" = "headless" ]; then
    echo "Starting in headless mode..."
    shift # remove first argument
    cd /app/Chrome
    python YouTubeBot_Headless.py "$@"
elif [ "$1" = "gui" ]; then
    echo "Starting with GUI..."
    cd /app/Chrome  
    python YouTubeBot_Docker.py
else
    # Default to GUI
    echo "Starting with GUI (default)..."
    cd /app/Chrome
    python YouTubeBot_Docker.py
fi

# Cleanup on exit
trap 'kill $XVFB_PID $WM_PID 2>/dev/null' EXIT