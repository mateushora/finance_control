import os
import logging
import pytesseract
import pandas as pd
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionExtractor(ABC):
    """Base class for all transaction extractors."""

    def __init__(self):
        # Ensure Tesseract is installed and accessible
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error("Tesseract OCR is not installed or not in PATH. Please install it first.")
            raise e
    
    def extract_text(self, file_path: str) -> pd.DataFrame:
        """Process a file (image or PDF) and return the extracted text."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext == '.png':
            text = self.extract_text_from_image(file_path)
        else:
            raise ValueError("Unsupported file format. Only PDF and PNG files are supported")
        
        return text
    
    @abstractmethod
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file."""
        pass
    
    @abstractmethod
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image file."""
        pass
