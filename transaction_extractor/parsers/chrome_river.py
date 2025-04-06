import re
import pandas as pd
from .base import TransactionParser

class ChromeRiverParser(TransactionParser):
    def __init__(self):
        """Initialize ChromeRiver parser with valid descriptions."""
        super().__init__()

        self.valid_descriptions = ['Hotel', 'Meals/Drinks']
        self.total_amount = None

        self.classification_rules = {
            'Hotel': ['Viagens', 'BCG'],
            'Meals/Drinks': ['Alimentação', 'Restaurante'],
        }

    def clean_text(self, text: str) -> str:
        """Clean up text to improve parsing."""
        # Remove content after total amount
        total_pattern = r'(.*?TotalPayMeAmount\s*\d{1,3}(?:,\d{3})*\.\d{2}).*'
        match = re.match(total_pattern, text, re.DOTALL)
        if match:
            text = match.group(1)
        
        # Split into lines and clean each line
        lines = text.split('\n')
        cleaned_lines = []
        current_group = []
        
        for line in lines:
            # Clean up horizontal whitespace
            line = re.sub(r'[ \t]+', ' ', line)
            line = line.strip()
            
            # Remove thousand separators from amounts
            line = re.sub(r'(\d),(\d{3}(?:\.\d{2})?)', r'\1\2', line)
            
            # Remove 'G' suffix from amounts
            line = re.sub(r'(\d+\.\d{2})G', r'\1', line)

            # Add white space after the date
            line = re.sub(r'(\d{2}/\d{2}/\d{4})', r'\1 ', line)
            
            if line:  # If line is not empty
                current_group.append(line)
            else:  # If line is empty
                if current_group:  # If we have accumulated lines
                    joined_line = ' '.join(current_group)
                    # Handle multiple amounts in joined line
                    amounts = re.findall(r'\d+\.\d{2}', joined_line)
                    if len(amounts) > 1:
                        # Replace all amounts except the last one with empty string
                        for amount in amounts[:-1]:
                            joined_line = joined_line.replace(amount, '', 1)
                        joined_line = re.sub(r'\s+', ' ', joined_line)  # Clean up any extra spaces
                        joined_line = joined_line.strip()
                    cleaned_lines.append(joined_line)
                    current_group = []
                cleaned_lines.append('')  # Keep the blank line
        
        # Don't forget to add the last group if it exists
        if current_group:
            joined_line = ' '.join(current_group)
            # Handle multiple amounts in last joined line
            amounts = re.findall(r'\d+\.\d{2}', joined_line)
            if len(amounts) > 1:
                for amount in amounts[:-1]:
                    joined_line = joined_line.replace(amount, '', 1)
                joined_line = re.sub(r'\s+', ' ', joined_line)
                joined_line = joined_line.strip()
            cleaned_lines.append(joined_line)
        
        # Remove any trailing empty lines
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)

    def parse(self, text: str) -> pd.DataFrame:
        """Parse ChromeRiver expense report text into a structured DataFrame."""
        # Clean the text first
        text = self.clean_text(text)
        
        # Initialize lists to store extracted data
        dates = []
        descriptions = []
        amounts = []
        categories = []
        subcategories = []
        
        # Regular expressions for matching
        date_pattern = r'\b(\d{2}/\d{2}/\d{4})\b'
        amount_pattern = r'\b(\d{1,5}(?:,\d{3})*\.\d{2})\b'
        total_pattern = r'TotalPayMeAmount\s*(\d{1,5}(?:,\d{3})*\.\d{2})'
        
        # Split text into lines and process each line
        lines = text.split('\n')
        for line in lines:
            # Find date
            date_match = re.search(date_pattern, line)
            if date_match:
                # Look for amount and description in the same line
                amounts_in_line = re.findall(amount_pattern, line)
                
                # Find description
                desc = None
                for valid_desc in self.valid_descriptions:
                    if valid_desc in line:
                        desc = valid_desc
                        break
                
                if desc and amounts_in_line:
                    dates.append(date_match.group(1))
                    descriptions.append(desc)
                    # Use the first amount found in the line
                    amounts.append(float(amounts_in_line[0].replace(',', '')))

                    category, subcategory = self._classify_transaction(desc, amounts_in_line[0])
                    categories.append(category)
                    subcategories.append(subcategory)
        
        # Extract total amount
        total_match = re.search(total_pattern, text)
        if total_match:
            self.total_amount = float(total_match.group(1).replace(',', ''))
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': pd.to_datetime(dates),
            'description': descriptions,
            'amount': amounts,
            'category': categories,
            'subcategory': subcategories,
        })
        
        if not self.check_consistency(df):
            raise ValueError("Inconsistent data: Final balance doesn't match the sum of transactions")

        if not self._check_categories(df):
            raise ValueError("Invalid categories found in transactions")

        return self.prettify(df)

    def check_consistency(self, df: pd.DataFrame) -> bool:
        """Check if the sum of transactions matches the total amount."""
        if not self.total_amount:
            raise ValueError("Total amount not found")
    
        transactions_sum = df['amount'].sum()
        return abs(transactions_sum - self.total_amount) <= 0.01  # Allow small floating-point differences
