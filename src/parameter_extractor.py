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
            str: Extracted text or empty string on failure
        """
        try:
            if self.ocr_engine == 'tesseract':
                # Tesseract OCR
                # Configure for French language:  lang='fra+eng'
                text = pytesseract.image_to_string(image_path, lang='fra+eng')
            else: 
                # EasyOCR
                result = self.reader.readtext(image_path)
                text = ' '.join([item[1] for item in result])
            
            # Check if text is empty
            if not text or text.strip() == '':
                print(f"⚠ Warning: No text extracted from {Path(image_path).name}")
                return ""
            
            return text
            
        except Exception as e:
            print(f"❌ OCR Error for {Path(image_path).name}: {e}")
            return ""
    
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
            'fluoro_time': r'[Ff]luoro.*?time.*?[:\s]+([0-9]+[.,]?[0-9]*)\s*(min|s)',
            'total_fluoro_kair': r'[Tt]otal.*?[Ff]luoro.*?[Kk]air.*?[:\s]+([0-9]+[.,]?[0-9]*)',
            'dose_entree_peau_max': r'[Dd]ose.*?entr[ée]e.*?peau.*?max.*?[:\s]+([0-9]+[.,]?[0-9]*)',
            'exposit_ni': r'[Ee]xposit.*?NI.*?[:\s]+([0-9]+[.,]?[0-9]*)',
            'total_pds': r'[Tt]otal.*?PDS.*?[:\s]+([0-9]+[.,]?[0-9]*)',
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
            dict: Extracted parameters (with None for failed extractions)
        """
        try:
            print(f"Extracting from: {Path(image_path).name}")
            
            # Check if file exists
            if not Path(image_path).exists():
                print(f"❌ Error: File not found: {image_path}")
                return self._get_empty_parameters(Path(image_path).name)
            
            # Extract text
            text = self.extract_text(image_path)
            
            # Check if OCR returned text
            if not text or text.strip() == '':
                print(f"⚠ Warning: OCR returned no text for {Path(image_path).name}")
                return self._get_empty_parameters(Path(image_path).name)
            
            # Parse parameters
            parameters = self.parse_parameters(text)
            
            # Add image filename
            parameters['image_file'] = Path(image_path).name
            
            # Count successfully extracted parameters
            extracted_count = sum(1 for v in parameters.values() if v is not None and v != Path(image_path).name)
            print(f"  ✓ Extracted {extracted_count}/7 parameters")
            
            return parameters
            
        except Exception as e:
            print(f"❌ Extraction failed for {Path(image_path).name}: {e}")
            return self._get_empty_parameters(Path(image_path).name)
    
    def _get_empty_parameters(self, filename):
        """Return empty parameter dict for failed extractions"""
        return {
            'image_file': filename,
            'fluoro_time': None,
            'total_fluoro_kair': None,
            'dose_entree_peau_max': None,
            'exposit_ni': None,
            'total_pds': None,
            'total_dose': None,
            'frequence_acquisition': None
        }
    
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
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
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

    def extract_from_cropped_regions(self, image_path):
        """
        Extract parameters by cropping each parameter's region individually.

        Uses RegionCropper to obtain sub-images, preprocesses each one with
        ImageProcessor.preprocess_sub_image(), runs Tesseract on each, and
        parses the first numeric value found.  Falls back to the full-image
        regex approach when no crop regions are configured.

        Args:
            image_path (str): Path to the full dose report image

        Returns:
            dict: Extracted parameter values keyed by parameter name
        """
        try:
            import cv2
            from src.region_cropper import RegionCropper
            from src.image_processor import ImageProcessor

            cropper = RegionCropper()
            image = cv2.imread(str(image_path))

            if image is None:
                print(f"❌ Error: Could not load image: {image_path}")
                return self._get_empty_parameters(Path(image_path).name)

            crops = cropper.crop_parameter_regions(image)

            # If no crop regions defined, fall back to full-image approach
            if not crops:
                return self.extract_from_image(image_path)

            processor = ImageProcessor(str(image_path))
            parameters = self._get_empty_parameters(Path(image_path).name)
            numeric_re = re.compile(r'([0-9]+[.,]?[0-9]*)')

            for param_name, sub_image in crops.items():
                preprocessed = processor.preprocess_sub_image(sub_image)
                if preprocessed is None:
                    continue
                try:
                    text = pytesseract.image_to_string(
                        preprocessed, lang='fra+eng',
                        config='--psm 7 --oem 3'
                    )
                    match = numeric_re.search(text)
                    if match:
                        value_str = match.group(1).replace(',', '.')
                        parameters[param_name] = float(value_str)
                except Exception as e:
                    print(f"  ⚠ OCR failed for {param_name}: {e}")

            extracted_count = sum(
                1 for k, v in parameters.items()
                if v is not None and k != 'image_file'
            )
            print(f"  ✓ Extracted {extracted_count}/7 parameters (cropped mode)")
            return parameters

        except ImportError as e:
            print(f"⚠ Cannot use cropped extraction ({e}), falling back to full-image mode")
            return self.extract_from_image(image_path)
        except Exception as e:
            print(f"❌ Cropped extraction failed for {Path(image_path).name}: {e}")
            return self._get_empty_parameters(Path(image_path).name)


if __name__ == "__main__":
    # Example usage
    extractor = ParameterExtractor(ocr_engine='tesseract')
    
    # Extract from single image
    params = extractor.extract_from_image('data/raw/example_image.png')
    print(params)
    
    # Batch extraction
    # df = extractor.batch_extract('data/raw/', 'data/processed/extracted_parameters.csv')
    # print(df.head())