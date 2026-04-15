#!/bin/bash
set -e

# Start virtual display (Xvfb)
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -nolisten tcp &
sleep 2

# Start VNC server on port 5900 (for QR code scanning)
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 &
sleep 1

echo "=========================================="
echo "  Virtual display started on :99"
echo "  VNC available on port 5900"
echo "  Connect with any VNC viewer to scan QR"
echo "  e.g. localhost:5900"
echo "=========================================="
echo "Starting Job Forwarder Agent..."

# Run the agent
exec python main.py
