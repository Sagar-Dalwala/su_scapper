# Enhanced PDF to DOCX Converter

This tool converts PDF files to DOCX format while preserving formatting, layout, images, and tables similar to how ilovepdf.com works.

## Features

- Maintains original PDF formatting in the output DOCX file
- Preserves images, tables, fonts, and layout
- Handles page sizes and orientation
- Includes a fallback method if the primary conversion fails
- Simple command-line interface
- Supports batch conversion of multiple files
- Can automatically organize PDFs and DOCX files into separate folders

## Installation

1. Make sure you have Python 3.7+ installed
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

### Single File Conversion

```bash
python enhanced_pdf_to_docx.py path/to/your/file.pdf
```

This will create a DOCX file in the same location with the same name (e.g., `file.docx`).

### Specifying Output Path

```bash
python enhanced_pdf_to_docx.py path/to/your/file.pdf --output path/to/output.docx
```

or use the short form:

```bash
python enhanced_pdf_to_docx.py path/to/your/file.pdf -o path/to/output.docx
```

### Organizing Files into Separate Folders

You can have PDFs and DOCX files automatically organized into separate folders:

```bash
python enhanced_pdf_to_docx.py path/to/your/file.pdf --organize
```

This will:
- Convert the PDF to DOCX
- Create a 'pdfs' folder and move the original PDF there
- Create a 'pdf_to_docx' folder and move the converted DOCX there

You can customize the folder names:

```bash
python enhanced_pdf_to_docx.py path/to/your/file.pdf --organize --pdf-folder="PDF_Files" --docx-folder="DOCX_Files"
```

### Batch Conversion

For converting multiple PDF files at once, use the batch conversion script:

```bash
python batch_pdf_to_docx.py path/to/pdf/directory
```

#### Batch Conversion Options

- Convert all PDFs in a directory:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory
  ```

- Specify output directory:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory --output-dir path/to/output/directory
  ```

- Process subdirectories recursively:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory --recursive
  ```

- Preserve directory structure in output:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory --output-dir path/to/output --keep-structure
  ```

- Control number of parallel workers:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory --workers 4
  ```

- Organize files into separate folders:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory --organize
  ```

- Customize folder names when organizing:
  ```bash
  python batch_pdf_to_docx.py path/to/pdf/directory --organize --pdf-folder="PDF_Files" --docx-folder="DOCX_Files"
  ```

### Standalone File Organization

If you already have PDF and DOCX files that need organization, you can use the dedicated organization script:

```bash
python organize_pdfs_and_docx.py path/to/directory
```

Options:
- Specify custom folder names:
  ```bash
  python organize_pdfs_and_docx.py --pdf-folder="PDF_Files" --docx-folder="DOCX_Files"
  ```
- Process subdirectories recursively:
  ```bash
  python organize_pdfs_and_docx.py --recursive
  ```

## How It Works

The tool uses the `pdf2docx` library which provides high-quality PDF to DOCX conversion that:

1. Preserves the visual layout of the PDF
2. Maintains tables, images, and graphics
3. Keeps text formatting including fonts, sizes, and styles
4. Handles different page orientations and sizes

If the primary conversion method fails, the tool falls back to a simpler method using PyPDF2 and python-docx that preserves as much formatting as possible.

## Troubleshooting

If you encounter any issues:

1. Check the log files (`enhanced_pdf_to_docx_conversion.log` or `batch_pdf_to_docx_conversion.log`) for error details
2. Make sure your PDF isn't corrupted or password-protected
3. Try updating the packages in requirements.txt
4. For complex PDFs with unusual elements, results may vary

## Limitations

- Some complex PDF features (JavaScript, 3D objects, etc.) cannot be converted
- Password-protected PDFs must be unlocked before conversion
- Very complex layouts might have slight differences in the output 