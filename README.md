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

The application can be run with the following command-line arguments:

```bash
python -m transaction_extractor -b <bank_name> -f <file_path> [-o <output_path>]
```

### Arguments

- `-b, --bank`: (Required) Specify the bank name. Available options:
  - `itau`: Itaú bank statements
  - `inter`: Inter bank statements
  - `nubank`: Nubank statements
  - `picpay`: PicPay statements
  - `splitwise`: Splitwise statements
  - `creditas`: Creditas statements
  - `chromeriver`: Chrome River expense reports

- `-f, --file`: (Required) Path to the bank statement file (PDF or image)

- `-o, --output`: (Optional) Path to save the output Excel file. If not provided, defaults to `data/{bank}_transactions.xlsx`

### Examples

1. Process an Itaú bank statement:
   ```bash
   python -m transaction_extractor -b itau -f path/to/statement.pdf
   ```

2. Process a Nubank statement with custom output path:
   ```bash
   python -m transaction_extractor -b nubank -f path/to/statement.pdf -o my_transactions.xlsx
   ```

## Customization

The application currently supports multiple bank statements through dedicated parsers. To add support for other banks:

1. Create a new parser class in `transaction_extractor/parsers/` that inherits from `BaseParser`
2. Implement the required parsing methods for your bank's format
3. Register your parser in `transaction_extractor/extractor.py`

## Features

- Supports PDF and image files
- Image preprocessing for better OCR accuracy
- Structured output in pandas DataFrame format
- Automatic Excel export
- Error handling and logging
- Multiple bank support

## Notes

- The accuracy of the extraction depends on the quality of the input files
- You may need to adjust the preprocessing steps based on your specific documents
- The transaction parsing logic should be customized to match your bank's statement format
