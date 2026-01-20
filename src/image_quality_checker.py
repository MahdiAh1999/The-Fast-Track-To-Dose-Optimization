"""
Image Quality Checker Module
Validates image quality before OCR processing to prevent errors
"""

import cv2
import numpy as np
from pathlib import Path
import pandas as pd
from typing import Dict, Tuple, List
import json


class ImageQualityChecker:
    """Assess image quality before processing to ensure accurate OCR"""
    
    # Quality thresholds
    MIN_RESOLUTION = (800, 600)  # Minimum width x height
    MIN_BRIGHTNESS = 50
    MAX_BRIGHTNESS = 200
    MIN_CONTRAST = 30
    MIN_SHARPNESS = 100
    
    def __init__(self, image_path: str):
        """
        Initialize quality checker
        
        Args:
            image_path (str): Path to the image file
        """
        self.image_path = image_path
        self.image = None
        self.quality_report = {}
        
    def load_image(self) -> bool:
        """Load image for quality assessment"""
        try:
            self.image = cv2.imread(self.image_path)
            if self.image is None:
                raise ValueError(f"Could not load image: {self.image_path}")
            return True
        except Exception as e:
            print(f"Error loading image: {e}")
            return False
    
    def check_resolution(self) -> Dict[str, any]:
        """
        Check if image resolution is sufficient for OCR
        
        Returns:
            dict: Resolution check results
        """
        if self.image is None:
            return {"status": "error", "message": "No image loaded"}
        
        height, width = self.image.shape[:2]
        
        is_adequate = (width >= self.MIN_RESOLUTION[0] and 
                      height >= self.MIN_RESOLUTION[1])
        
        return {
            "width": width,
            "height": height,
            "is_adequate": is_adequate,
            "status": "pass" if is_adequate else "fail",
            "message": f"Resolution: {width}x{height} - {'✓ Adequate' if is_adequate else '✗ Too low'}"
        }
    
    def check_brightness(self) -> Dict[str, any]:
        """
        Check if image brightness is within acceptable range
        
        Returns:
            dict: Brightness check results
        """
        if self.image is None:
            return {"status": "error", "message": "No image loaded"}
        
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Calculate mean brightness
        mean_brightness = np.mean(gray)
        
        is_adequate = (self.MIN_BRIGHTNESS <= mean_brightness <= self.MAX_BRIGHTNESS)
        
        status = "pass"
        if mean_brightness < self.MIN_BRIGHTNESS:
            status = "fail"
            message = f"Brightness: {mean_brightness:.1f} - ✗ Too dark"
        elif mean_brightness > self.MAX_BRIGHTNESS:
            status = "fail"
            message = f"Brightness: {mean_brightness:.1f} - ✗ Too bright"
        else:
            message = f"Brightness: {mean_brightness:.1f} - ✓ Good"
        
        return {
            "mean_brightness": mean_brightness,
            "is_adequate": is_adequate,
            "status": status,
            "message": message
        }
    
    def check_contrast(self) -> Dict[str, any]:
        """
        Check if image has sufficient contrast
        
        Returns:
            dict: Contrast check results
        """
        if self.image is None:
            return {"status": "error", "message": "No image loaded"}
        
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Calculate standard deviation as a measure of contrast
        contrast = np.std(gray)
        
        is_adequate = contrast >= self.MIN_CONTRAST
        
        return {
            "contrast_std": contrast,
            "is_adequate": is_adequate,
            "status": "pass" if is_adequate else "fail",
            "message": f"Contrast: {contrast:.1f} - {'✓ Good' if is_adequate else '✗ Too low'}"
        }
    
    def check_sharpness(self) -> Dict[str, any]:
        """
        Check image sharpness using Laplacian variance
        
        Returns:
            dict: Sharpness check results
        """
        if self.image is None:
            return {"status": "error", "message": "No image loaded"}
        
        # Convert to grayscale
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        
        # Calculate Laplacian variance (measure of sharpness)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        is_adequate = sharpness >= self.MIN_SHARPNESS
        
        return {
            "sharpness_score": sharpness,
            "is_adequate": is_adequate,
            "status": "pass" if is_adequate else "fail",
            "message": f"Sharpness: {sharpness:.1f} - {'✓ Sharp' if is_adequate else '✗ Blurry'}"
        }
    
    def check_aspect_ratio(self) -> Dict[str, any]:
        """
        Check if aspect ratio is reasonable
        
        Returns:
            dict: Aspect ratio check results
        """
        if self.image is None:
            return {"status": "error", "message": "No image loaded"}
        
        height, width = self.image.shape[:2]
        aspect_ratio = width / height
        
        # Typical screen aspect ratios: 4:3 to 21:9
        is_reasonable = 1.0 <= aspect_ratio <= 3.0
        
        return {
            "aspect_ratio": aspect_ratio,
            "is_reasonable": is_reasonable,
            "status": "pass" if is_reasonable else "warning",
            "message": f"Aspect ratio: {aspect_ratio:.2f} - {'✓ Normal' if is_reasonable else '⚠ Unusual'}"
        }
    
    def run_all_checks(self) -> Dict[str, any]:
        """
        Run all quality checks
        
        Returns:
            dict: Complete quality assessment report
        """
        if not self.load_image():
            return {"overall_status": "error", "message": "Failed to load image"}
        
        self.quality_report = {
            "image_path": self.image_path,
            "resolution": self.check_resolution(),
            "brightness": self.check_brightness(),
            "contrast": self.check_contrast(),
            "sharpness": self.check_sharpness(),
            "aspect_ratio": self.check_aspect_ratio()
        }
        
        # Determine overall status
        critical_checks = ["resolution", "brightness", "contrast", "sharpness"]
        failed_checks = [check for check in critical_checks 
                        if self.quality_report[check]["status"] == "fail"]
        
        if len(failed_checks) == 0:
            overall_status = "pass"
            overall_message = "✓ All quality checks passed"
        elif len(failed_checks) <= 1:
            overall_status = "warning"
            overall_message = f"⚠ Minor issues detected: {', '.join(failed_checks)}"
        else:
            overall_status = "fail"
            overall_message = f"✗ Multiple quality issues: {', '.join(failed_checks)}"
        
        self.quality_report["overall_status"] = overall_status
        self.quality_report["overall_message"] = overall_message
        self.quality_report["failed_checks"] = failed_checks
        
        return self.quality_report
    
    def print_report(self):
        """Print quality assessment report in a readable format"""
        if not self.quality_report:
            print("No quality report available. Run run_all_checks() first.")
            return
        
        print("\n" + "="*60)
        print(f"IMAGE QUALITY REPORT: {Path(self.image_path).name}")
        print("="*60)
        
        for check_name in ["resolution", "brightness", "contrast", "sharpness", "aspect_ratio"]:
            if check_name in self.quality_report:
                print(f"  {self.quality_report[check_name]['message']}")
        
        print("-"*60)
        print(f"  {self.quality_report['overall_message']}")
        print("="*60 + "\n")
    
    def save_report(self, output_path: str):
        """Save quality report to JSON file"""
        if not self.quality_report:
            print("No quality report to save. Run run_all_checks() first.")
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.quality_report, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False


def batch_quality_check(input_folder: str, output_report_path: str = None) -> pd.DataFrame:
    """
    Run quality checks on all images in a folder
    
    Args:
        input_folder (str): Path to folder containing images
        output_report_path (str): Optional path to save summary report
        
    Returns:
        pd.DataFrame: Summary of quality checks for all images
    """
    input_path = Path(input_folder)
    
    if not input_path.exists():
        print(f"Error: Folder not found: {input_folder}")
        return None
    
    # Supported image formats
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    image_files = [f for f in input_path.iterdir() 
                   if f.suffix.lower() in image_extensions]
    
    if len(image_files) == 0:
        print(f"No images found in {input_folder}")
        return None
    
    print(f"\nChecking quality of {len(image_files)} images...\n")
    
    results = []
    
    for img_file in image_files:
        checker = ImageQualityChecker(str(img_file))
        report = checker.run_all_checks()
        checker.print_report()
        
        results.append({
            'filename': img_file.name,
            'overall_status': report['overall_status'],
            'resolution': f"{report['resolution']['width']}x{report['resolution']['height']}",
            'brightness': f"{report['brightness']['mean_brightness']:.1f}",
            'contrast': f"{report['contrast']['contrast_std']:.1f}",
            'sharpness': f"{report['sharpness']['sharpness_score']:.1f}",
            'failed_checks': ', '.join(report['failed_checks']) if report['failed_checks'] else 'None'
        })
    
    # Create DataFrame
    df_results = pd.DataFrame(results)
    
    # Print summary
    print("\n" + "="*60)
    print("BATCH QUALITY CHECK SUMMARY")
    print("="*60)
    print(f"Total images: {len(image_files)}")
    print(f"Passed: {len(df_results[df_results['overall_status'] == 'pass'])}")
    print(f"Warnings: {len(df_results[df_results['overall_status'] == 'warning'])}")
    print(f"Failed: {len(df_results[df_results['overall_status'] == 'fail'])}")
    print("="*60 + "\n")
    
    # Save report if output path provided
    if output_report_path:
        df_results.to_csv(output_report_path, index=False)
        print(f"✓ Quality report saved to: {output_report_path}")
    
    return df_results


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        output_report = sys.argv[2] if len(sys.argv) > 2 else "quality_report.csv"
        batch_quality_check(folder_path, output_report)
    else:
        print("Usage: python image_quality_checker.py <folder_path> [output_report.csv]")
