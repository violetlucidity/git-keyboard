#!/usr/bin/env bash
# Git Keyboard launcher for Raspberry Pi
# Place a symlink or shortcut to this file on your desktop.

set -e
cd "$(dirname "$0")"

# Install Flask if needed
if ! python3 -c "import flask" 2>/dev/null; then
  echo "Installing Flask..."
  pip3 install flask -q
fi

# Read port from config
PORT=$(python3 -c "import json; print(json.load(open('config-git-keyboard.json'))['port'])")

# Start server in background
python3 keyboard_server.py &
SERVER_PID=$!
echo "Server PID: $SERVER_PID (port $PORT)"

# Give server a moment to bind
sleep 1

# Open browser — try common Pi browsers in order
URL="http://127.0.0.1:$PORT"
if command -v chromium-browser &>/dev/null; then
  chromium-browser --kiosk "$URL" &
elif command -v chromium &>/dev/null; then
  chromium --kiosk "$URL" &
elif command -v firefox &>/dev/null; then
  firefox "$URL" &
elif command -v midori &>/dev/null; then
  midori "$URL" &
else
  echo "No browser found. Open $URL manually."
fi

# Keep script alive; kill server when done
trap "kill $SERVER_PID 2>/dev/null" EXIT
wait $SERVER_PID
