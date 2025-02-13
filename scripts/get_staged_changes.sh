#!/bin/bash

# EuroTempl System
# Copyright (c) 2024 Pygmalion Records

# Get current timestamp
timestamp=$(date +"%Y%m%d_%H%M%S")
output_file="staged_changes_${timestamp}.txt"

# Write header
echo "EuroTempl Staged Changes - $(date)" > "$output_file"
echo "=================================" >> "$output_file"
echo "" >> "$output_file"

# Get list of staged files
git diff --cached --name-only | while read -r file; do
    echo "File: $file" >> "$output_file"
    echo "-------------------" >> "$output_file"
    git diff --cached "$file" >> "$output_file"
    echo "" >> "$output_file"
    echo "" >> "$output_file"
done

echo "Staged changes have been saved to $output_file"