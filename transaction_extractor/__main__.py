import logging
import argparse
from .extractor import TransactionExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Example usage of the TransactionExtractor class."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Extract transactions from bank statements.')
    parser.add_argument('-b', '--bank', 
                      required=True,
                      choices=['itau', 'inter', 'nubank', 'picpay', 'splitwise', 'creditas'],
                      help='Bank name to process statements from')
    parser.add_argument('-f', '--file',
                      required=True,
                      help='Path to the bank statement file')
    parser.add_argument('-o', '--output',
                      help='Path to save the output Excel file (default: data/{bank}_transactions.xlsx)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Initialize extractor
    extractor = TransactionExtractor(bank=args.bank)
    
    try:
        # Process the file
        df = extractor.process_file(args.file)
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