#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

# Create the public directory if it doesn't exist
if [ ! -d "public" ]; then
  mkdir "public"
fi

# Run the python script to copy the files
python3 src/main.py

echo "Copied static files to public directory"

# Start a simple web server
cd public
python3 -m http.server 8888