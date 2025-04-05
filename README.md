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
2. Run the script:
   ```bash
   python transaction_extractor.py
   ```

3. The script will:
   - Process the file
   - Extract transaction information
   - Save the results to a CSV file named `transactions.csv`

## Customization

The current implementation includes basic transaction parsing. You may need to customize the `parse_transactions` method in `transaction_extractor.py` to match your specific bank statement format. Look for patterns in your bank statements and adjust the parsing logic accordingly.

## Features

- Supports both PDF and image files (JPG, JPEG, PNG, BMP)
- Image preprocessing for better OCR accuracy
- Structured output in pandas DataFrame format
- Automatic CSV export
- Error handling and logging

## Notes

- The accuracy of the extraction depends on the quality of the input files
- You may need to adjust the preprocessing steps based on your specific documents
- The transaction parsing logic should be customized to match your bank's statement format 
