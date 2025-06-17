#!/bin/bash

# Create telemetry_data directory if it doesn't exist
mkdir -p telemetry_data
mkdir -p "session_data"

# Define source directory
SOURCE_DIR_TELEM="../backend/telemetry_data"
SOURCE_DIR_SESSION="../backend/session_data"

# Move all CSV and JSON files from source directory to current telemetry_data directory
find "$SOURCE_DIR_TELEM" -type f \( -name "*.csv" -o -name "*.json" \) -exec cp {} ./telemetry_data/ \;
find "$SOURCE_DIR_SESSION" -type f \( -name "*.json" \) -exec cp {} ./session_data/ \;