#!/bin/bash

echo "Starting Face-Off Game..."
echo ""
echo "This will open two browser windows:"
echo "- Game interface"
echo "- Admin panel"
echo ""
echo "Press Enter to continue..."
read

# Run the Python startup script
python3 startup.py

# Keep terminal open if there's an error
if [ $? -ne 0 ]; then
    echo ""
    echo "An error occurred. Please check the above messages."
    read -p "Press Enter to exit..."
fi