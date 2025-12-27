"""
Parameter Extractor Module
Extracts dosimetric parameters from images using OCR
"""

import pytesseract
import easyocr
import re
import pandas as pd
from pathlib import Path
import numpy as np


class ParameterExtractor: 
    """Extract dosimetric parameters from processed images"""
    
    def __init__(self, ocr_engine='tesseract'):
        """
        Initialize the parameter extractor
        
        Args:
            ocr_engine (str): 'tesseract' or 'easyocr'
        """
        self.ocr_engine = ocr_engine
        self.reader = None
        
        if ocr_engine == 'easyocr':
            # Initialize EasyOCR reader (supports French and English)
            self.reader = easyocr.Reader(['fr', 'en'])
    
    def extract_text(self, image_path):
        """
        Extract text from image using selected OCR engine
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            str: Extracted text
        """
        if self.ocr_engine == 'tesseract':
            # Tesseract OCR
            # Configure for French language:  lang='fra+eng'
            text = pytesseract.image_to_string(image_path, lang='fra+eng')
        else: 
            # EasyOCR
            result = self.reader.readtext(image_path)
            text = ' '.join([item[1] for item in result])
        
        return text
    
    def parse_parameters(self, text):
        """
        Parse dosimetric parameters from extracted text
        
        Args: 
            text (str): OCR extracted text
            
        Returns: 
            dict: Dictionary of extracted parameters
        """
        parameters = {
            'fluoro_time':  None,
            'total_fluoro_kair': None,
            'dose_entree_peau_max': None,
            'exposit_ni': None,
            'total_pds': None,
            'total_dose': None,
            'frequence_acquisition': None
        }
        
        # Patterns to match parameters (adjust based on your actual image format)
        patterns = {
            'fluoro_time':  r'[Ff]luoro.*? time.*?[:\s]+([0-9]+[.,]?[0-9]*)\s*(min|s)',
            'total_fluoro_kair': r'[Tt]otal.*?[Ff]luoro.*?[Kk]air.*?[:\s]+([0-9]+[.,]?[0-9]*)',
            'dose_entree_peau_max': r'[Dd]ose.*?entr[ée]e.*?peau.*?max.*?[:\s]+([0-9]+[.,]?[0-9]*)',
            'exposit_ni': r'[Ee]xposit.*?NI.*?[:\s]+([0-9]+[.,]? [0-9]*)',
            'total_pds': r'[Tt]otal.*? PDS.*?[:\s]+([0-9]+[.,]? [0-9]*)',
            'total_dose': r'[Tt]otal.*?[Dd]ose.*?[:\s]+([0-9]+[.,]?[0-9]*)',
            'frequence_acquisition': r'[Ff]r[ée]quence.*?acquisition.*?[:\s]+([0-9]+[.,]?[0-9]*)\s*[Ff]/[Ss]'
        }
        
        # Extract each parameter
        for param_name, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Extract numeric value and convert comma to dot
                value_str = match.group(1).replace(',', '.')
                try:
                    parameters[param_name] = float(value_str)
                except ValueError:
                    parameters[param_name] = None
        
        return parameters
    
    def extract_from_image(self, image_path):
        """
        Complete extraction pipeline for a single image
        
        Args:
            image_path (str): Path to the image
            
        Returns:
            dict:  Extracted parameters
        """
        print(f"Extracting from: {Path(image_path).name}")
        
        # Extract text
        text = self.extract_text(image_path)
        
        # Parse parameters
        parameters = self.parse_parameters(text)
        
        # Add image filename
        parameters['image_file'] = Path(image_path).name
        
        return parameters
    
    def batch_extract(self, image_folder, output_csv):
        """
        Extract parameters from all images in a folder
        
        Args:
            image_folder (str): Path to folder containing images
            output_csv (str): Path to save CSV output
            
        Returns:
            pd.DataFrame: DataFrame with all extracted parameters
        """
        # Get all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(Path(image_folder).glob(f'*{ext}'))
            image_files.extend(Path(image_folder).glob(f'*{ext.upper()}'))
        
        print(f"Found {len(image_files)} images to process\n")
        
        # Extract parameters from each image
        all_parameters = []
        
        for img_path in image_files:
            params = self.extract_from_image(str(img_path))
            all_parameters.append(params)
            print(f"  ✓ Completed: {img_path.name}\n")
        
        # Create DataFrame
        df = pd.DataFrame(all_parameters)
        
        # Reorder columns
        column_order = [
            'image_file',
            'fluoro_time',
            'total_fluoro_kair',
            'dose_entree_peau_max',
            'exposit_ni',
            'total_pds',
            'total_dose',
            'frequence_acquisition'
        ]
        df = df[column_order]
        
        # Save to CSV
        df.to_csv(output_csv, index=False)
        print(f"\n✅ Results saved to: {output_csv}")
        
        return df


if __name__ == "__main__": 
    # Example usage
    extractor = ParameterExtractor(ocr_engine='tesseract')
    
    # Extract from single image
    params = extractor.extract_from_image('data/raw/example_image. png')
    print(params)
    
    # Batch extraction
    # df = extractor.batch_extract('data/raw/', 'data/processed/extracted_parameters.csv')
    # print(df. head())