#!/usr/bin/env bash
# build.sh – compile main.py into a standalone binary with PyInstaller
# Usage: bash build.sh

set -e

# 1. Make sure PyInstaller is available
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "[build] Installing PyInstaller..."
    pip install pyinstaller
fi

# 2. Make sure python-dotenv is available (needed at runtime inside the binary)
if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "[build] Installing python-dotenv..."
    pip install python-dotenv
fi

# 3. Compile
echo "[build] Compiling main.py -> dist/twitch-storage ..."
pyinstaller \
    --onefile \
    --name twitch-storage \
    --hidden-import dotenv \
    main.py

echo ""
echo "[build] Done!  Binary is at: dist/twitch-storage"
echo ""
echo "Usage examples:"
echo "  ./dist/twitch-storage upload path/to/file.png"
echo "  ./dist/twitch-storage upload path/to/file.png --chunk-size 300 --delay 2.0"
echo "  ./dist/twitch-storage download <VOD_ID> recovered.png"
