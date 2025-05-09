#!/bin/bash

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to the directory
cd "$DIR"

# Run the startup script
python3 startup.py

# Keep Terminal window open
echo
echo "Press any key to close..."
read -n 1