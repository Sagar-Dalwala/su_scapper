import os
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import sys

def check_conversion_status(pdf_dir='output/pdfs', csv_dir='csv_output'):
    """Check the status of PDF to CSV conversion"""
    
    if not os.path.exists(pdf_dir) or not os.path.exists(csv_dir):
        print(f"Error: One or both directories don't exist: {pdf_dir}, {csv_dir}")
        return
    
    # Count PDF files
    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    pdf_count = len(pdf_files)
    
    # Count CSV files (raw and structured)
    raw_csv_files = [f for f in os.listdir(csv_dir) if f.lower().endswith('_raw.csv')]
    structured_csv_files = [f for f in os.listdir(csv_dir) if f.lower().endswith('_structured.csv')]
    
    # Calculate completion percentage
    raw_completion = (len(raw_csv_files) / pdf_count) * 100 if pdf_count > 0 else 0
    structured_completion = (len(structured_csv_files) / pdf_count) * 100 if pdf_count > 0 else 0
    
    print(f"Conversion Status:")
    print(f"Total PDF files: {pdf_count}")
    print(f"Raw CSV files generated: {len(raw_csv_files)} ({raw_completion:.2f}%)")
    print(f"Structured CSV files generated: {len(structured_csv_files)} ({structured_completion:.2f}%)")
    
    # Calculate average file sizes
    if raw_csv_files:
        raw_sizes = [os.path.getsize(os.path.join(csv_dir, f)) / 1024 for f in raw_csv_files]  # KB
        avg_raw_size = sum(raw_sizes) / len(raw_sizes)
        print(f"Average raw CSV file size: {avg_raw_size:.2f} KB")
    
    if structured_csv_files:
        structured_sizes = [os.path.getsize(os.path.join(csv_dir, f)) / 1024 for f in structured_csv_files]  # KB
        avg_structured_size = sum(structured_sizes) / len(structured_sizes)
        print(f"Average structured CSV file size: {avg_structured_size:.2f} KB")
    
    # List any PDFs that haven't been converted yet
    converted_bases = [Path(f).stem.replace('_raw', '') for f in raw_csv_files]
    not_converted = [pdf for pdf in pdf_files if Path(pdf).stem not in converted_bases]
    
    if not_converted:
        print(f"\nPDFs waiting to be converted ({len(not_converted)}):")
        for pdf in not_converted[:10]:  # Show first 10
            print(f"- {pdf}")
        if len(not_converted) > 10:
            print(f"... and {len(not_converted) - 10} more")

def check_csv_quality(csv_dir='csv_output', sample_size=5):
    """Check the quality of the generated CSV files"""
    
    if not os.path.exists(csv_dir):
        print(f"Error: Directory doesn't exist: {csv_dir}")
        return
    
    # Get structured CSV files
    structured_csv_files = [f for f in os.listdir(csv_dir) if f.lower().endswith('_structured.csv')]
    
    if not structured_csv_files:
        print("No structured CSV files found for quality check.")
        return
    
    # Sample a few files for quality check
    samples = structured_csv_files[:sample_size] if len(structured_csv_files) > sample_size else structured_csv_files
    
    print(f"\nQuality check on {len(samples)} sample files:")
    
    quality_metrics = {
        'total_rows': [],
        'filled_content': [],
        'has_course_title': [],
        'has_objectives': [],
        'has_units': []
    }
    
    for csv_file in samples:
        file_path = os.path.join(csv_dir, csv_file)
        try:
            df = pd.read_csv(file_path)
            
            # Calculate metrics
            total_rows = len(df)
            filled_content = sum(df['content'].notna()) / total_rows if total_rows > 0 else 0
            has_course_title = 'Course Title' in df['section'].values
            has_objectives = 'Objectives' in df['section'].values
            has_units = 'Unit' in df['section'].values
            
            # Store metrics
            quality_metrics['total_rows'].append(total_rows)
            quality_metrics['filled_content'].append(filled_content * 100)  # as percentage
            quality_metrics['has_course_title'].append(has_course_title)
            quality_metrics['has_objectives'].append(has_objectives)
            quality_metrics['has_units'].append(has_units)
            
            print(f"\nFile: {csv_file}")
            print(f"- Total rows: {total_rows}")
            print(f"- Content cells filled: {filled_content * 100:.2f}%")
            print(f"- Has course title: {'Yes' if has_course_title else 'No'}")
            print(f"- Has objectives: {'Yes' if has_objectives else 'No'}")
            print(f"- Has units: {'Yes' if has_units else 'No'}")
            
        except Exception as e:
            print(f"Error analyzing {csv_file}: {str(e)}")
    
    # Calculate overall quality metrics
    avg_rows = sum(quality_metrics['total_rows']) / len(quality_metrics['total_rows']) if quality_metrics['total_rows'] else 0
    avg_content_fill = sum(quality_metrics['filled_content']) / len(quality_metrics['filled_content']) if quality_metrics['filled_content'] else 0
    pct_has_title = sum(quality_metrics['has_course_title']) / len(quality_metrics['has_course_title']) * 100 if quality_metrics['has_course_title'] else 0
    pct_has_objectives = sum(quality_metrics['has_objectives']) / len(quality_metrics['has_objectives']) * 100 if quality_metrics['has_objectives'] else 0
    pct_has_units = sum(quality_metrics['has_units']) / len(quality_metrics['has_units']) * 100 if quality_metrics['has_units'] else 0
    
    print("\nOverall Quality Metrics:")
    print(f"- Average rows per file: {avg_rows:.2f}")
    print(f"- Average content fill rate: {avg_content_fill:.2f}%")
    print(f"- Files with course title: {pct_has_title:.2f}%")
    print(f"- Files with objectives: {pct_has_objectives:.2f}%")
    print(f"- Files with unit information: {pct_has_units:.2f}%")

def combine_csv_files(csv_dir='csv_output', output_file='combined_syllabus_data.csv'):
    """Combine all structured CSV files into a single file for AI training"""
    
    if not os.path.exists(csv_dir):
        print(f"Error: Directory doesn't exist: {csv_dir}")
        return
    
    # Get structured CSV files
    structured_csv_files = [f for f in os.listdir(csv_dir) if f.lower().endswith('_structured.csv')]
    
    if not structured_csv_files:
        print("No structured CSV files found for combining.")
        return
    
    combined_data = []
    
    for csv_file in structured_csv_files:
        file_path = os.path.join(csv_dir, csv_file)
        try:
            df = pd.read_csv(file_path)
            
            # Add file name as a column to identify the source
            df['source_file'] = Path(csv_file).stem.replace('_structured', '')
            
            combined_data.append(df)
            
        except Exception as e:
            print(f"Error reading {csv_file}: {str(e)}")
    
    if not combined_data:
        print("No data to combine.")
        return
    
    # Combine all dataframes
    combined_df = pd.concat(combined_data, ignore_index=True)
    
    # Save combined data
    combined_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"Combined data saved to {output_file}")
    print(f"Total rows in combined file: {len(combined_df)}")
    
def main():
    command = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    if command == "status":
        check_conversion_status()
    elif command == "quality":
        check_csv_quality()
    elif command == "combine":
        combine_csv_files()
    elif command == "all":
        check_conversion_status()
        check_csv_quality()
        combine_csv_files()
    else:
        print("Invalid command. Use 'status', 'quality', 'combine', or 'all'.")

if __name__ == "__main__":
    main() 