"""
Image Processor Module
Handles loading and preprocessing of dosimetric screenshots
"""

import cv2
import numpy as np
from PIL import Image
import os
from pathlib import Path


class ImageProcessor:
    """Process dosimetric screenshots for OCR extraction"""
    
    def __init__(self, image_path):
        """
        Initialize the image processor
        
        Args: 
            image_path (str): Path to the image file
        """
        self. image_path = image_path
        self.original_image = None
        self. processed_image = None
        
    def load_image(self):
        """Load image from file"""
        try: 
            self.original_image = cv2.imread(self.image_path)
            if self.original_image is None:
                raise ValueError(f"Could not load image:  {self.image_path}")
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def preprocess_for_ocr(self):
        """
        Preprocess image to improve OCR accuracy
        - Convert to grayscale
        - Apply thresholding
        - Denoise
        """
        if self.original_image is None:
            print("No image loaded.  Call load_image() first.")
            return None
        
        # Convert to grayscale
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to get better contrast
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        self.processed_image = denoised
        return self.processed_image
    
    def save_processed_image(self, output_path):
        """Save the processed image"""
        if self. processed_image is not None:
            cv2.imwrite(output_path, self. processed_image)
            return True
        return False
    
    def display_images(self):
        """Display original and processed images side by side"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, 2, figsize=(12, 6))
        
        # Original
        axes[0].imshow(cv2.cvtColor(self. original_image, cv2.COLOR_BGR2RGB))
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # Processed
        axes[1].imshow(self.processed_image, cmap='gray')
        axes[1].set_title('Processed Image')
        axes[1].axis('off')
        
        plt. tight_layout()
        plt.show()


def batch_preprocess_images(input_folder, output_folder):
    """
    Preprocess all images in a folder
    
    Args:
        input_folder (str): Path to folder containing raw images
        output_folder (str): Path to save processed images
    """
    # Create output folder if it doesn't exist
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    # Get all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '. tiff']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(Path(input_folder).glob(f'*{ext}'))
        image_files.extend(Path(input_folder).glob(f'*{ext.upper()}'))
    
    print(f"Found {len(image_files)} images to process")
    
    # Process each image
    for img_path in image_files: 
        print(f"Processing: {img_path. name}")
        
        processor = ImageProcessor(str(img_path))
        if processor.load_image():
            processor.preprocess_for_ocr()
            
            # Save with same name in output folder
            output_path = Path(output_folder) / img_path.name
            processor. save_processed_image(str(output_path))
            print(f"  ✓ Saved to: {output_path}")
    
    print("\n✅ Batch processing complete!")


if __name__ == "__main__": 
    # Example usage
    processor = ImageProcessor("data/raw/example_image.png")
    processor.load_image()
    processor.preprocess_for_ocr()
    processor.display_images()