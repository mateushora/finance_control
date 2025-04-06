import logging
import argparse
from .extractors import (
    ItauExtractor,
    ChromeRiverExtractor
)
from .parsers import (
    ItauParser,
    ChromeRiverParser
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Example usage of the transaction extractors."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract transactions from bank statements.')
    parser.add_argument('-b', '--bank', 
                      required=True,
                      choices=['itau', 'inter', 'nubank', 'picpay', 'splitwise', 'creditas', 'chrome_river'],
                      help='Bank name to process statements from')
    parser.add_argument('-f', '--file',
                      required=True,
                      help='Path to the bank statement file')
    parser.add_argument('-o', '--output',
                      help='Path to save the output Excel file (default: data/{bank}_transactions.xlsx)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize appropriate extractor based on bank
    extractors = {
        'itau': ItauExtractor,
        'chrome_river': ChromeRiverExtractor,
        # Add other extractors as they are implemented
    }

    # Initialize appropriate parser based on bank
    parsers = {
        'itau': ItauParser,
        'chrome_river': ChromeRiverParser,
        # Add other parsers as they are implemented
    }
    
    extractor_class = extractors.get(args.bank.lower())
    if not extractor_class:
        raise ValueError(f"No extractor implemented for bank: {args.bank}")
    
    parser_class = parsers.get(args.bank.lower())
    if not parser_class:
        raise ValueError(f"No parser implemented for bank: {args.bank}")

    extractor = extractor_class()
    parser = parser_class()
    
    try:
        # Process the file
        text = extractor.extract_text(args.file)
        df = parser.parse(text)
        print("\nExtracted Transactions:")
        print(df)
        
        # Determine output path
        output_path = args.output or f"data/{args.bank}_transactions.xlsx"
        
        # Save to Excel
        df.to_excel(output_path, index=False)
        print(f"\nTransactions saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 