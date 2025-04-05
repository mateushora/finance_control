# Bank Transaction Extractor

This application extracts bank transaction information from images and PDF files using OCR (Optical Character Recognition) and converts them into a structured pandas DataFrame.

## Prerequisites

Before using this application, you need to install:

1. Tesseract OCR:
   - On macOS: `brew install tesseract`
   - On Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - On Windows: Download and install from [Tesseract's GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)

2. Poppler (required for PDF processing):
   - On macOS: `brew install poppler`
   - On Ubuntu/Debian: `sudo apt-get install poppler-utils`
   - On Windows: Download and install from [Poppler's website](https://poppler.freedesktop.org/)

3. Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Place your bank statement files (PDF or images) in a directory
2. Run the module:
   ```bash
   python -m transaction_extractor
   ```

3. The script will:
   - Process the file
   - Extract transaction information
   - Save the results to a CSV file named `transactions.xlsx`

## Customization

The application currently supports Itaú bank statements through a dedicated parser. To add support for other banks:

1. Create a new parser class in `transaction_extractor/parsers/` that inherits from `BaseParser`
2. Implement the required parsing methods for your bank's format
3. Register your parser in `transaction_extractor/extractor.py`

## Features

- Currently only supports PDF files
- Image preprocessing for better OCR accuracy
- Structured output in pandas DataFrame format
- Automatic Excel export
- Error handling and logging

## Notes

- The accuracy of the extraction depends on the quality of the input files
- You may need to adjust the preprocessing steps based on your specific documents
- The transaction parsing logic should be customized to match your bank's statement format 
