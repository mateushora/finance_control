import logging
from .extractor import TransactionExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Example usage of the TransactionExtractor class."""
    # Example: Process an Inter bank statement
    extractor = TransactionExtractor(bank='itau')
    
    try:
        # Replace with your file path
        file_path = "/Users/horamateus/Personal/finance_app/data/extrato-lancamentos.pdf"
        df = extractor.process_file(file_path)
        print("\nExtracted Transactions:")
        print(df)
        
        # Save to CSV
        output_path = "transactions.xlsx"
        df.to_excel(output_path, index=False)
        print(f"\nTransactions saved to {output_path}")
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main() 