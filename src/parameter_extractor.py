"""
Parameter Extractor Module
Extracts dosimetric parameters from images using OCR
"""

import pytesseract
import easyocr
import re
import json
import logging
import pandas as pd
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class ParameterExtractor: 
    """Extract dosimetric parameters from processed images"""
    
    def __init__(self, ocr_engine='tesseract', config_path='config.json'):
        """
        Initialize the parameter extractor
        
        Args:
            ocr_engine (str): 'tesseract' or 'easyocr'
            config_path (str): Path to the configuration file
        """
        self.ocr_engine = ocr_engine
        self.reader = None
        self._range_checks = {}
        self._procedure_type = 'coronary_angiography'
        self._total_extracted = 0
        self._total_valid = 0

        # Load range checks and study metadata from config
        try:
            config_file = Path(config_path)
            if not config_file.is_absolute():
                # Resolve relative to project root (parent of src/)
                config_file = Path(__file__).parent.parent / config_path
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            self._range_checks = cfg.get('range_checks', {})
            self._procedure_type = cfg.get('study', {}).get('procedure_type', 'coronary_angiography')
        except Exception as e:
            logger.warning(f"Could not load config for range checks: {e}")

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
            'pka': None,
            'kair': None,
            'fluoro_time':  None,
            'total_fluoro_kair': None,
            'dose_entree_peau_max': None,
            'exposit_ni': None,
            'total_pds': None,
            'total_dose': None,
            'frequence_acquisition': None,
            'procedure_type': self._procedure_type
        }
        
        # Patterns to match parameters (adjust based on your actual image format)
        patterns = {
            'pka': [
                r'PKA.*?[:\s]+([0-9]+[.,]?[0-9]*)\s*(µGy|uGy|mGy)?',
                r'[Pp]roduit.*?[Kk]erma.*?[:\s]+([0-9]+[.,]?[0-9]*)'
            ],
            'kair': [
                r'[Kk]a[,.]?r.*?[:\s]+([0-9]+[.,]?[0-9]*)',
                r'[Kk]erma.*?[Rr][eé]f[eé]rence.*?[:\s]+([0-9]+[.,]?[0-9]*)'
            ],
            'fluoro_time':  [r'[Ff]luoro.*? time.*?[:\s]+([0-9]+[.,]?[0-9]*)\s*(min|s)'],
            'total_fluoro_kair': [r'[Tt]otal.*?[Ff]luoro.*?[Kk]air.*?[:\s]+([0-9]+[.,]?[0-9]*)'],
            'dose_entree_peau_max': [r'[Dd]ose.*?entr[ée]e.*?peau.*?max.*?[:\s]+([0-9]+[.,]?[0-9]*)'],
            'exposit_ni': [r'[Ee]xposit.*?NI.*?[:\s]+([0-9]+[.,]? [0-9]*)'],
            'total_pds': [r'[Tt]otal.*? PDS.*?[:\s]+([0-9]+[.,]? [0-9]*)'],
            'total_dose': [r'[Tt]otal.*?[Dd]ose.*?[:\s]+([0-9]+[.,]?[0-9]*)'],
            'frequence_acquisition': [r'[Ff]r[ée]quence.*?acquisition.*?[:\s]+([0-9]+[.,]?[0-9]*)\s*[Ff]/[Ss]']
        }
        
        # Extract each parameter — try each pattern until one matches
        for param_name, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace(',', '.')
                    try:
                        parameters[param_name] = float(value_str)
                    except ValueError:
                        parameters[param_name] = None
                    break
        
        return parameters
    
    def apply_range_checks(self, parameters):
        """
        Validate extracted values against configured ranges (post-OCR safeguard).

        Values outside the expected range are set to None and logged.
        This mirrors the poster's description of 2 errors (0.57%) caught by the
        range-checking post-processing safeguard.

        Args:
            parameters (dict): Extracted parameter dict (modified in-place)

        Returns:
            dict: The same dict with out-of-range values set to None
        """
        for param, range_cfg in self._range_checks.items():
            if param not in parameters:
                continue
            value = parameters[param]
            if value is None:
                continue
            min_val = range_cfg.get('min')
            max_val = range_cfg.get('max')
            unit = range_cfg.get('unit', '')
            out_of_range = (min_val is not None and value < min_val) or \
                           (max_val is not None and value > max_val)
            if out_of_range:
                logger.warning(
                    f"Post-processing safeguard: {param}={value} {unit} is outside "
                    f"expected range [{min_val}, {max_val}]. Value set to None."
                )
                print(
                    f"  ⚠ Range-check safeguard: {param}={value} {unit} "
                    f"out of range [{min_val}, {max_val}] — flagged as invalid"
                )
                parameters[param] = None
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

            # Post-OCR range-checking safeguard
            parameters = self.apply_range_checks(parameters)
            
            # Add image filename
            parameters['image_file'] = Path(image_path).name
            
            # Count successfully extracted parameters (exclude metadata fields)
            numeric_params = [k for k in parameters if k not in ('image_file', 'procedure_type')]
            extracted_count = sum(1 for k in numeric_params if parameters[k] is not None)
            total_params = len(numeric_params)
            self._total_extracted += total_params
            self._total_valid += extracted_count
            print(f"  ✓ Extracted {extracted_count}/{total_params} parameters")
            
            return parameters
            
        except Exception as e:
            print(f"❌ Extraction failed for {Path(image_path).name}: {e}")
            return self._get_empty_parameters(Path(image_path).name)
    
    def _get_empty_parameters(self, filename):
        """Return empty parameter dict for failed extractions"""
        return {
            'image_file': filename,
            'pka': None,
            'kair': None,
            'fluoro_time': None,
            'total_fluoro_kair': None,
            'dose_entree_peau_max': None,
            'exposit_ni': None,
            'total_pds': None,
            'total_dose': None,
            'frequence_acquisition': None,
            'procedure_type': self._procedure_type
        }

    def get_extraction_accuracy(self):
        """
        Return overall extraction accuracy across all processed images.

        Returns:
            tuple: (total_valid, total_extracted, accuracy_pct)
        """
        if self._total_extracted == 0:
            return (0, 0, 0.0)
        accuracy = (self._total_valid / self._total_extracted) * 100
        return (self._total_valid, self._total_extracted, accuracy)
    
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
        
        # Reorder columns — PKA and Ka,r first among numeric parameters
        column_order = [
            'image_file',
            'procedure_type',
            'pka',
            'kair',
            'fluoro_time',
            'total_fluoro_kair',
            'dose_entree_peau_max',
            'exposit_ni',
            'total_pds',
            'total_dose',
            'frequence_acquisition'
        ]
        # Only include columns that actually exist in the dataframe
        column_order = [c for c in column_order if c in df.columns]
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