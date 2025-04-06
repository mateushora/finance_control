from abc import ABC, abstractmethod
import pandas as pd
import yaml

class TransactionParser(ABC):
    """Abstract base class for bank-specific transaction parsers."""
    
    def __init__(self):
        """Initialize the parser with categories and classification rules."""
        # Load categories from YAML
        with open('transaction_extractor/categories.yaml', 'r') as f:
            self.categories = yaml.safe_load(f)['categories']
        
        # Define classification rules (description patterns -> [category, subcategory])
        self.classification_rules = {}

        # Define conditional rules based on description and amount
        self.conditional_rules = []

    def _classify_transaction(self, description: str, amount: float) -> tuple:
        """Classify a transaction based on its description and amount."""
        # First check conditional rules that depend on both description and amount
        for rule in self.conditional_rules:
            if (rule['description'] in description and 
                rule['amount_range'][0] <= abs(amount) <= rule['amount_range'][1]):
                return rule['category'], rule['subcategory']

        # Then check exact description matches
        for pattern, classification in self.classification_rules.items():
            if pattern in description:
                return classification[0], classification[1]
        
        # If no match found, return as unidentified
        return 'Não Identificado', None

    def _check_categories(self, df: pd.DataFrame) -> bool:
        """
        Check if all categories in the DataFrame match those defined in categories.yaml.
        
        Args:
            df: DataFrame containing transactions with 'category' and 'subcategory' columns
            
        Returns:
            bool: True if all categories are valid, False otherwise
        """
        # Get unique categories from DataFrame
        df_categories = df['category'].unique()
        
        # Check if each category exists in YAML categories
        for category in df_categories:
            if category != 'Não Identificado' and category not in self.categories:
                return False
            
            # If category exists, check its subcategories
            if category != 'Não Identificado':
                # Get subcategories for transactions with this category
                df_subcategories = df[df['category'] == category]['subcategory'].unique()
                
                # Get valid subcategories from YAML
                valid_subcategories = self.categories[category]
                
                # Check each subcategory
                for subcategory in df_subcategories:
                    # Skip None/empty subcategories
                    if pd.isna(subcategory) or subcategory == '':
                        continue
                        
                    if subcategory not in valid_subcategories:
                        return False
        
        return True

    @abstractmethod
    def check_consistency(self, df: pd.DataFrame) -> bool:
        """
        Check if the parsed data is consistent.
        Returns True if data is consistent, False otherwise.
        Each parser should implement its own consistency checks.
        """
        pass

    @abstractmethod
    def parse(self, text: str) -> pd.DataFrame:
        """Parse the extracted text into a structured DataFrame of transactions."""
        pass

    @abstractmethod
    def clean_text(self, text: str) -> str:
        """
        Clean and standardize the input text before parsing.
        Each parser should implement its own text cleaning logic.

        Args:
            text: Raw text extracted from statement

        Returns:
            Cleaned text ready for parsing
        """
        pass

    def prettify(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the DataFrame into a standardized format with specific columns.
        
        Returns:
            pd.DataFrame with columns: year, month, day, bank, category, subcategory, description, amount
        """
        # Extract year, month, and day from date column
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day
        
        # Add bank column
        df['bank'] = self.__class__.__name__.replace('Parser', '')

        # Replace Itau with Itaú in bank name
        df['bank'] = df['bank'].replace('Itau', 'Itaú')

        # Select and order columns
        formatted_df = df[[
            'year', 'month', 'day', 'bank', 'category', 'subcategory', 
            'description', 'amount'
        ]]
        
        return formatted_df 