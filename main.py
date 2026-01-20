"""
Main Pipeline Script
Complete workflow from raw images to DRL calculation
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.image_quality_checker import batch_quality_check
from src.image_processor import batch_preprocess_images
from src.parameter_extractor import ParameterExtractor
from src.statistical_analyzer import StatisticalAnalyzer


def main():
    """
    Execute the complete DRL calculation pipeline
    """
    print("="*70)
    print(" AUTOMATED DRL ESTABLISHMENT PIPELINE")
    print("="*70)
    
    # Define paths
    raw_images_path = 'data/raw/'
    processed_images_path = 'data/processed/'
    quality_report_path = 'data/quality_reports/quality_report.csv'
    extracted_data_path = 'results/extracted_parameters.csv'
    drls_output_path = 'results/drls/local_drls.csv'
    
    # Check if raw images exist
    if not Path(raw_images_path).exists() or len(list(Path(raw_images_path).glob('*.*'))) == 0:
        print("\n❌ ERROR: No images found in data/raw/")
        print("Please place your dosimetric screenshots in the data/raw/ folder.")
        return
    
    # ========================================================================
    # PHASE 1: IMAGE QUALITY ASSESSMENT
    # ========================================================================
    print("\n" + "="*70)
    print("PHASE 1: IMAGE QUALITY ASSESSMENT")
    print("="*70)
    
    try:
        df_quality = batch_quality_check(raw_images_path, quality_report_path)
        
        if df_quality is None:
            print("❌ Quality check failed. Please review your images.")
            return
        
        # Count images by status
        passed = len(df_quality[df_quality['overall_status'] == 'pass'])
        warnings = len(df_quality[df_quality['overall_status'] == 'warning'])
        failed = len(df_quality[df_quality['overall_status'] == 'fail'])
        
        print(f"\n✓ Quality assessment complete:")
        print(f"  - {passed} images passed")
        print(f"  - {warnings} images with warnings")
        print(f"  - {failed} images failed")
        
        if failed > 0:
            print(f"\n⚠ WARNING: {failed} image(s) failed quality checks.")
            print(f"Review the report at: {quality_report_path}")
            response = input("Continue with processing? (y/n): ")
            if response.lower() != 'y':
                print("Processing cancelled. Please fix image quality issues first.")
                return
    
    except Exception as e:
        print(f"❌ Error during quality assessment: {e}")
        return
    
    # ========================================================================
    # PHASE 2: IMAGE PREPROCESSING
    # ========================================================================
    print("\n" + "="*70)
    print("PHASE 2: IMAGE PREPROCESSING")
    print("="*70)
    
    try:
        batch_preprocess_images(raw_images_path, processed_images_path)
        print("✓ All images preprocessed successfully")
    
    except Exception as e:
        print(f"❌ Error during preprocessing: {e}")
        return
    
    # ========================================================================
    # PHASE 3: PARAMETER EXTRACTION
    # ========================================================================
    print("\n" + "="*70)
    print("PHASE 3: PARAMETER EXTRACTION")
    print("="*70)
    
    try:
        extractor = ParameterExtractor(ocr_engine='tesseract')
        results_df = extractor.batch_extract(processed_images_path, extracted_data_path)
        
        if results_df is not None:
            print(f"✓ Extracted parameters from {len(results_df)} images")
            print(f"✓ Results saved to: {extracted_data_path}")
        else:
            print("❌ Parameter extraction failed")
            return
    
    except Exception as e:
        print(f"❌ Error during parameter extraction: {e}")
        return
    
    # ========================================================================
    # PHASE 4: STATISTICAL ANALYSIS & DRL CALCULATION
    # ========================================================================
    print("\n" + "="*70)
    print("PHASE 4: STATISTICAL ANALYSIS & DRL CALCULATION")
    print("="*70)
    
    try:
        analyzer = StatisticalAnalyzer(extracted_data_path)
        
        if not analyzer.load_data():
            print("❌ Failed to load extracted data")
            return
        
        # Calculate descriptive statistics
        stats = analyzer.calculate_descriptive_stats()
        print("\nDescriptive Statistics:")
        print(stats)
        
        # Calculate DRLs (3rd quartile)
        drls = analyzer.calculate_drls()
        print("\n" + "="*70)
        print("DIAGNOSTIC REFERENCE LEVELS (DRLs) - 75th Percentile")
        print("="*70)
        for param, value in drls.items():
            print(f"  {param}: {value:.2f}")
        
        # Save DRLs
        analyzer.save_drls(drls_output_path)
        
        # Generate visualizations
        print("\nGenerating visualizations...")
        analyzer.visualize_distributions('results/visualizations/')
        print("✓ Visualizations saved to results/visualizations/")
    
    except Exception as e:
        print(f"❌ Error during statistical analysis: {e}")
        return
    
    # ========================================================================
    # PIPELINE COMPLETE
    # ========================================================================
    print("\n" + "="*70)
    print("✓ PIPELINE COMPLETE!")
    print("="*70)
    print("\nResults saved to:")
    print(f"  - Quality report: {quality_report_path}")
    print(f"  - Extracted parameters: {extracted_data_path}")
    print(f"  - DRLs: {drls_output_path}")
    print(f"  - Visualizations: results/visualizations/")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
