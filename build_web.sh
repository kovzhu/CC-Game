#!/bin/bash
# Install pygbag if not already installed
pip install pygbag

# Build the web version
# --build: creates the build folder
# --archive: archives the assets
echo "Building web version..."
pygbag --build main.py

echo "Build complete! Check the 'build/web' folder."
echo "You can test it locally by running: pygbag main.py"
