import re
import pandas as pd
from .base import TransactionParser

class ItauParser(TransactionParser):
    def __init__(self):
        """Initialize the parser with classification rules."""
        super().__init__()
        
        # Define classification rules (description patterns -> [category, subcategory])
        self.classification_rules = {
            'PIX TRANSF FELIPE': ['Cuidados Pessoais', 'Academia'],
            'REMUNERACAO/SALARIO': ['Receitas', 'Salário'],
            'PIX TRANSF Mateus': ['Transferência entre Contas', ''],
        }

        # Define conditional rules based on description and amount
        self.conditional_rules = [
            {
                'description': 'MOBILEPAG TIT BANCO',
                'amount_range': (3800, 3900),
                'category': 'Despesas Essenciais',
                'subcategory': 'Aluguel/IPTU'
            },
            {
                'description': 'MOBILEPAG TIT BANCO',
                'amount_range': (780, 800),
                'category': 'Despesas Essenciais',
                'subcategory': 'Condomínio'
            }
        ]

    def clean_text(self, text: str) -> str:
        """Clean the text by removing unwanted content."""
        lines = text.split('\n')
        cleaned_lines = []
        start_processing = False
        
        for line in lines:
            # Start processing when we find "SALDO INICIAL"
            if "SALDO INICIAL" in line:
                start_processing = True
            
            # Only process lines if we've started
            if start_processing:
                # Remove all special characters
                line = re.sub(r'[(\[\]|)]', ' ', line)
                
                # Remove thousand separators from numbers
                line = re.sub(r'(\d+)\.(\d+,\d{2})', r'\1\2', line)

                # Remove whitespaces from beginning and end of line
                line = line.strip()

                # Remove any special characters from the end of the line
                line = re.sub(r'[^\w\s]$', '', line)

                # Remove double spaces
                line = re.sub(r'\s+', ' ', line)

                # Change special characters after the date to a space
                line = re.sub(r'(\d{2}/\d{2}/\d{4})[^\w\s]', r'\1 ', line)
                
                cleaned_lines.append(line)

                if "SALDO FINAL" in line:
                    break
        
        return '\n'.join(cleaned_lines) 

    def parse(self, text: str) -> pd.DataFrame:
        """Parse Itaú bank statements."""
        # Clean the text first
        cleaned_text = self.clean_text(text)
        
        transactions = []
        lines = cleaned_text.split('\n')
        
        for line in lines:
            if not line.strip():
                continue
            
            # Itaú specific parsing logic
            # Format: "DD/MM/YYYY Description Amount"
            match = re.match(r'(\d{2}/\d{2}/\d{4})\s+(.*?)\s+([-+]?\d+,\d{2})', line)
            if match:
                date, description, amount = match.groups()
                amount_float = float(amount.replace(',', '.'))
                category, subcategory = self._classify_transaction(description.strip(), amount_float)
                transactions.append({
                    'date': date,
                    'description': description.strip(),
                    'amount': amount.replace(',', '.'),
                    'category': category,
                    'subcategory': subcategory
                })
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y')
        df['amount'] = df['amount'].astype(float)
        
        # Check consistency of the parsed data
        if not self.check_consistency(df):
            raise ValueError("Inconsistent data: Final balance doesn't match the sum of transactions")
        
        # Check if all categories are valid according to categories.yaml
        if not self._check_categories(df):
            raise ValueError("Invalid categories found in transactions")

        # Format the DataFrame
        return self.prettify(df)

    def check_consistency(self, df: pd.DataFrame) -> bool:
        """
        Check if the parsed data is consistent by comparing the SALDO FINAL
        with the sum of all other transactions.
        """
        try:
            # Get the SALDO FINAL amount
            saldo_final = df[df['description'] == 'SALDO FINAL']['amount'].iloc[0]
            
            # Get the SALDO INICIAL amount
            saldo_inicial = df[df['description'] == 'SALDO INICIAL']['amount'].iloc[0]
            
            # Sum all transactions except SALDO INICIAL and SALDO FINAL
            mask = ~df['description'].isin(['SALDO INICIAL', 'SALDO FINAL'])
            transactions_sum = df[mask]['amount'].sum()
            
            # The final balance should equal initial balance plus all transactions
            expected_final = saldo_inicial + transactions_sum
            
            # Allow for small floating-point differences
            tolerance = 0.01
            return abs(saldo_final - expected_final) < tolerance
            
        except (IndexError, KeyError):
            # If we can't find SALDO INICIAL or SALDO FINAL, data is inconsistent
            return False
