#!/bin/bash

# Configuration
MAX_FILE_SIZE_MB=1        # Skip files larger than this size
MAX_TOTAL_SIZE_MB=50      # Maximum total output size
OUTPUT_DIR="ET_REPO_EXPORT"
TREE_FILE="ET_REPO_00_TREE.md"
MAX_FILES_PER_CHUNK=10    # Number of code files per output file

# Colors for better readability
BLUE='\033[0;34m'
NC='\033[0m'  # No Color

# Function to get human readable size
human_readable() {
    local size=$1
    if [[ $size -ge 1048576 ]]; then
        echo "$(( size / 1048576 ))MB"
    elif [[ $size -ge 1024 ]]; then
        echo "$(( size / 1024 ))KB"
    else
        echo "${size}B"
    fi
}

# Function to check if a file is ignored by git
is_ignored_by_git() {
    git check-ignore -q "$1"
    return $?
}

# Function to check file size
check_file_size() {
    local file="$1"
    local size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
    local max_size=$((MAX_FILE_SIZE_MB * 1024 * 1024))
    
    if [ "$size" -gt "$max_size" ]; then
        echo "Skipping large file: $file ($(human_readable $size))"
        return 1
    fi
    return 0
}

# Function to create the project tree
create_project_tree() {
    local output_file="$OUTPUT_DIR/$TREE_FILE"
    
    echo "# ET_REPO/ Project Tree" > "$output_file"
    echo "Generated on: $(date)" >> "$output_file"
    echo "\`\`\`" >> "$output_file"
    
    if command -v tree &> /dev/null; then
        tree -a -I ".git|$OUTPUT_DIR" --noreport | while read -r line; do
            if ! is_ignored_by_git "${line##* }"; then
                echo "$line" >> "$output_file"
            fi
        done
    else
        find . -not -path '*/\.git/*' -not -path "*/$OUTPUT_DIR/*" -print | while read -r file; do
            if ! is_ignored_by_git "$file"; then
                local depth=$(($(echo "$file" | tr -cd '/' | wc -c) - 1))
                printf "%${depth}s%s\n" "" "$(basename "$file")" >> "$output_file"
            fi
        done
    fi
    
    echo "\`\`\`" >> "$output_file"
}

# Function to export code files content
export_code_files() {
    local file_counter=0
    local chunk_counter=1
    local current_output_file
    local total_size=0
    local max_total_bytes=$((MAX_TOTAL_SIZE_MB * 1024 * 1024))
    
    # Find all .cpp and .py files, excluding git-ignored ones
    find . -type f \( -name "*.cpp" -o -name "*.py" \) \
        -not -path '*/\.git/*' \
        -not -path "*/$OUTPUT_DIR/*" | sort | while read -r file; do
        
        # Skip if file is ignored by git or too large
        if is_ignored_by_git "$file" || ! check_file_size "$file"; then
            continue
        fi
        
        # Create new chunk file if needed
        if [ $((file_counter % MAX_FILES_PER_CHUNK)) -eq 0 ]; then
            current_output_file="$OUTPUT_DIR/ET_REPO_$(printf "%02d" $chunk_counter)_code_files.md"
            echo "# ET_REPO/ Code Files (Part $chunk_counter)" > "$current_output_file"
            echo "Generated on: $(date)" >> "$current_output_file"
            ((chunk_counter++))
        fi
        
        # Add file content with Markdown formatting
        echo -e "\n## ${file#./}" >> "$current_output_file"
        echo -e "Path: \`$file\`  " >> "$current_output_file"
        echo -e "Size: $(human_readable $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file"))\n" >> "$current_output_file"
        
        # Add code block with syntax highlighting
        if [[ "$file" == *.py ]]; then
            echo "\`\`\`python" >> "$current_output_file"
        else
            echo "\`\`\`cpp" >> "$current_output_file"
        fi
        
        cat "$file" >> "$current_output_file"
        echo -e "\`\`\`\n" >> "$current_output_file"
        
        ((file_counter++))
        
        # Check total size
        total_size=$(du -b "$OUTPUT_DIR" | cut -f1)
        if [ "$total_size" -gt "$max_total_bytes" ]; then
            echo "Warning: Output size limit reached (${MAX_TOTAL_SIZE_MB}MB)"
            return 1
        fi
    done
}

# Main execution
main() {
    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo "Error: Not a git repository"
        exit 1
    fi
    
    # Create output directory
    rm -rf "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    echo -e "${BLUE}Creating project tree...${NC}"
    create_project_tree
    
    echo -e "${BLUE}Exporting code files...${NC}"
    export_code_files
    
    echo -e "${BLUE}Export completed. Files are in $OUTPUT_DIR/${NC}"
    echo "- Project tree: $TREE_FILE"
    echo "- Code files are split into chunks of $MAX_FILES_PER_CHUNK files each"
    echo "- Files larger than ${MAX_FILE_SIZE_MB}MB were skipped"
    echo "- Total output size limit: ${MAX_TOTAL_SIZE_MB}MB"
}

# Run the script
main