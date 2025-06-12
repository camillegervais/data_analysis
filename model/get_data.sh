#!/bin/bash

# Create telemetry_data directory if it doesn't exist
mkdir -p telemetry_data

# Define source directory
SOURCE_DIR="../backend/telemetry_data"

# Move all CSV and JSON files from source directory to current telemetry_data directory
find "$SOURCE_DIR" -type f \( -name "*.csv" -o -name "*.json" \) -exec cp {} ./telemetry_data/ \;