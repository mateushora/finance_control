import cv2
import logging
import pytesseract
import numpy as np
from .base import TransactionExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromeRiverExtractor(TransactionExtractor):
    """Extractor for Chrome River expense reports."""
    
    def __init__(self):
        """Initialize the Chrome River extractor."""
        super().__init__()

    def detect_tables(self, image: np.ndarray) -> list:
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
        
        # Apply thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        return thresh

    def extract_text_from_table(self, table_image: np.ndarray) -> str:
        """Extract text from a table image using OCR."""
        # Preprocess the table image
        processed_table = self.preprocess_table(table_image)
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6 -l eng'
        
        # Perform OCR
        text = pytesseract.image_to_string(
            processed_table,
            config=custom_config
        )
        
        return text

    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image file, focusing on tables."""
        try:
            # Read the image using OpenCV
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Could not read image file: {image_path}")
            
            # Detect tables in the image
            table_regions = self.detect_tables(image)
            if not table_regions:
                logger.warning("No tables detected in the image")
                return ""
            
            # Extract text from each table
            all_text = []
            for i, table in enumerate(table_regions):
                logger.info(f"Processing table {i+1} of {len(table_regions)}")
                text = self.extract_text_from_table(table)
                all_text.append(text)
            
            return "\n".join(all_text)
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            raise
