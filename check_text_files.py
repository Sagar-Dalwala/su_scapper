import os
import sys
import glob
from pathlib import Path

def list_extracted_files(text_dir='extracted_text'):
    """List all extracted text files"""
    if not os.path.exists(text_dir):
        print(f"Error: Directory {text_dir} doesn't exist")
        return
    
    text_files = [f for f in os.listdir(text_dir) if f.lower().endswith('.txt')]
    
    if not text_files:
        print("No text files found.")
        return
    
    print(f"Found {len(text_files)} text files:")
    
    # Sort files by size to identify potential conversion issues
    file_info = []
    for file in text_files:
        file_path = os.path.join(text_dir, file)
        size_kb = os.path.getsize(file_path) / 1024
        file_info.append((file, size_kb))
    
    # Sort by size
    file_info.sort(key=lambda x: x[1])
    
    # Print information
    for file, size_kb in file_info:
        print(f"{file} - {size_kb:.2f} KB")
    
    return file_info

def peek_file_content(file_path, lines=20):
    """View the beginning of a file"""
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} doesn't exist")
        return
    
    try:
        print(f"\nPreviewing first {lines} lines of {file_path}:")
        print("-" * 80)
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= lines:
                    break
                print(line.rstrip())
        
        print("-" * 80)
        
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def create_combined_file(text_dir='extracted_text', output_file='all_syllabus_content.txt'):
    """Combine all text files into a single large file for easier AI training"""
    if not os.path.exists(text_dir):
        print(f"Error: Directory {text_dir} doesn't exist")
        return
    
    text_files = [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.lower().endswith('.txt')]
    
    if not text_files:
        print("No text files found to combine.")
        return
    
    combined_content = []
    
    for file_path in text_files:
        try:
            # Add document separator
            combined_content.append("\n" + "="*80 + "\n")
            combined_content.append(f"DOCUMENT: {Path(file_path).stem}\n")
            combined_content.append("="*80 + "\n\n")
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                combined_content.append(content)
                combined_content.append("\n\n")
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
    
    # Write combined content to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(combined_content))
        
        print(f"Successfully created combined file: {output_file}")
        print(f"Total size: {os.path.getsize(output_file) / (1024*1024):.2f} MB")
    except Exception as e:
        print(f"Error creating combined file: {str(e)}")

def word_search(text_dir='extracted_text', search_term=None):
    """Search for specific keywords in all extracted text files"""
    if not search_term:
        print("No search term provided.")
        return
    
    if not os.path.exists(text_dir):
        print(f"Error: Directory {text_dir} doesn't exist")
        return
    
    text_files = [os.path.join(text_dir, f) for f in os.listdir(text_dir) if f.lower().endswith('.txt')]
    
    if not text_files:
        print("No text files found to search.")
        return
    
    results = []
    
    for file_path in text_files:
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Case-insensitive search
            if search_term.lower() in content.lower():
                # Count occurrences
                count = content.lower().count(search_term.lower())
                results.append((Path(file_path).stem, count))
        except Exception as e:
            print(f"Error searching {file_path}: {str(e)}")
    
    if results:
        # Sort by occurrence count (highest first)
        results.sort(key=lambda x: x[1], reverse=True)
        
        print(f"Found '{search_term}' in {len(results)} files:")
        for file_name, count in results:
            print(f"{file_name}: {count} occurrences")
    else:
        print(f"'{search_term}' not found in any files.")

def view_specific_file(filename, text_dir='extracted_text'):
    """Display contents of a specific file with a simple pager"""
    file_path = os.path.join(text_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} doesn't exist")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.readlines()
            
        page_size = 25  # Lines per page
        total_lines = len(content)
        
        page = 0
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
            
            start_line = page * page_size
            end_line = min(start_line + page_size, total_lines)
            
            print(f"File: {filename} | Page {page+1}/{(total_lines+page_size-1)//page_size} | Lines {start_line+1}-{end_line}/{total_lines}")
            print("-" * 80)
            
            for i in range(start_line, end_line):
                print(content[i].rstrip())
            
            print("-" * 80)
            print("Navigation: [n]ext page, [p]revious page, [q]uit")
            
            cmd = input("> ").lower()
            if cmd == 'q':
                break
            elif cmd == 'n' and end_line < total_lines:
                page += 1
            elif cmd == 'p' and page > 0:
                page -= 1
    
    except Exception as e:
        print(f"Error reading file: {str(e)}")

def main():
    if len(sys.argv) < 2:
        print("Available commands:")
        print("  list - List all extracted text files")
        print("  peek [filename] - View the beginning of a text file")
        print("  view [filename] - View a file with a simple pager")
        print("  combine - Combine all text files into one large file")
        print("  search [term] - Search for a term in all files")
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_extracted_files()
    elif command == "peek" and len(sys.argv) > 2:
        filename = sys.argv[2]
        if not filename.endswith('.txt'):
            filename += '.txt'
        peek_file_content(os.path.join('extracted_text', filename))
    elif command == "view" and len(sys.argv) > 2:
        filename = sys.argv[2]
        if not filename.endswith('.txt'):
            filename += '.txt'
        view_specific_file(filename)
    elif command == "combine":
        create_combined_file()
    elif command == "search" and len(sys.argv) > 2:
        search_term = sys.argv[2]
        word_search(search_term=search_term)
    else:
        print("Invalid command or missing parameters.")
        print("Usage:")
        print("  python check_text_files.py list")
        print("  python check_text_files.py peek [filename]")
        print("  python check_text_files.py view [filename]")
        print("  python check_text_files.py combine")
        print("  python check_text_files.py search [term]")

if __name__ == "__main__":
    main() 