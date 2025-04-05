import os
import cv2
import logging
import pytesseract
import numpy as np
from typing import List
from pdf2image import convert_from_path
from .parsers import (
    TransactionParser, InterParser, ItauParser, SplitwiseParser,
    PicPayParser, NubankParser, CreditasParser,
    ChromeRiverParser
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionExtractor:
    def __init__(self, bank: str):
        """Initialize the transaction extractor."""
        if not bank:
            raise ValueError("Bank parameter is required")
            
        # Ensure Tesseract is installed and accessible
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error("Tesseract OCR is not installed or not in PATH. Please install it first.")
            raise e
        
        # Initialize the appropriate parser based on the bank
        self.parser = self._get_parser(bank)

    def _get_parser(self, bank: str) -> TransactionParser:
        """Get the appropriate parser for the given bank."""
        parsers = {
            'itau': ItauParser,
            'inter': InterParser,
            'nubank': NubankParser,
            'picpay': PicPayParser,
            'splitwise': SplitwiseParser,
            'creditas': CreditasParser,
            'chrome_river': ChromeRiverParser
        }
        
        parser_class = parsers.get(bank.lower())
        if not parser_class:
            raise ValueError(f"Unsupported bank: {bank}")
        return parser_class()

    def detect_tables(self, image: np.ndarray) -> List[np.ndarray]:
        """Detect tables in the image and return their regions."""
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Detect horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
        
        # Detect horizontal lines
        horizontal_lines = cv2.erode(thresh, horizontal_kernel, iterations=1)
        horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=1)
        
        # Detect vertical lines
        vertical_lines = cv2.erode(thresh, vertical_kernel, iterations=1)
        vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=1)
        
        # Combine horizontal and vertical lines
        table_mask = cv2.add(horizontal_lines, vertical_lines)
        
        # Find contours of tables
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Sort contours by area and keep only the largest ones (likely tables)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)
        
        # Extract table regions
        table_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # Add some padding around the table
            padding = 10
            x = max(0, x - padding)
            y = max(0, y - padding)
            w = min(image.shape[1] - x, w + 2 * padding)
            h = min(image.shape[0] - y, h + 2 * padding)
            table_regions.append(image[y:y+h, x:x+w])
        
        return table_regions

    def preprocess_table(self, table_image: np.ndarray) -> np.ndarray:
        """Preprocess table image for better OCR."""
        # Convert to grayscale
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Remove noise
        kernel = np.ones((1, 1), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
        
        return opening

    def extract_text_from_table(self, table_image: np.ndarray) -> str:
        """Extract text from a table region."""
        # Preprocess the table
        processed_table = self.preprocess_table(table_image)
        
        # Configure Tesseract for table processing
        custom_config = r'--oem 3 --psm 6 -l eng+por'
        
        # Perform OCR
        text = pytesseract.image_to_string(
            processed_table,
            config=custom_config
        )
        
        return text

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file, focusing on tables."""
        try:
            # Convert PDF to images with higher DPI
            images = convert_from_path(
                pdf_path,
                dpi=300,
                grayscale=True,
                thread_count=4
            )
            
            all_text = []
            
            for i, image in enumerate(images):
                logger.info(f"Processing page {i+1} of {len(images)}")
                
                # Convert PIL image to OpenCV format
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Detect tables in the page
                table_regions = self.detect_tables(opencv_image)
                
                if not table_regions:
                    logger.warning(f"No tables detected on page {i+1}")
                    continue
                
                # Process each table
                for j, table in enumerate(table_regions):
                    logger.info(f"Processing table {j+1} on page {i+1}")
                    text = self.extract_text_from_table(table)
                    all_text.append(text)
            
            return "\n".join(all_text)
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {str(e)}")
            raise

    def process_file(self, file_path: str):
        """Process a file (image or PDF) and return a DataFrame of transactions."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        else:
            raise ValueError("Currently only PDF files are supported for table detection")
        
        return self.parser.parse(text) 