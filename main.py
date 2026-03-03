"""
Main Pipeline Script
Complete workflow from raw images to DRL calculation
Follows the flowchart architecture:
  Import image → Convert to 8-bit → Crop regions → Denoise/resize sub-images
  → OCR each sub-image → Store values → (loop) → Quartiles / Histograms / Excel
"""

import os
import sys
from pathlib import Path
import pandas as pd

# Add src directory to path
sys.path.append(str(Path(__file__).parent / 'src'))

from src.image_quality_checker import batch_quality_check
from src.image_processor import batch_preprocess_images, ImageProcessor
from src.region_cropper import RegionCropper
from src.parameter_extractor import ParameterExtractor
from src.statistical_analyzer import StatisticalAnalyzer


def _ensure_dirs(*paths):
    """Create directories (including parents) if they do not exist."""
    for p in paths:
        Path(p).mkdir(parents=True, exist_ok=True)


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
    excel_output_path = 'results/drls/full_report.xlsx'
    visualizations_path = 'results/visualizations/'

    # Create all required output directories upfront
    _ensure_dirs(
        processed_images_path,
        Path(quality_report_path).parent,
        Path(extracted_data_path).parent,
        Path(drls_output_path).parent,
        visualizations_path,
    )

    # Check if raw images exist
    if not Path(raw_images_path).exists() or \
            len(list(Path(raw_images_path).glob('*.*'))) == 0:
        print("\n❌ ERROR: No images found in data/raw/")
        print("Please place your dosimetric screenshots in the data/raw/ folder.")
        return

    # ====================================================================
    # PHASE 1: IMAGE QUALITY ASSESSMENT
    # ====================================================================
    print("\n" + "="*70)
    print("PHASE 1: IMAGE QUALITY ASSESSMENT")
    print("="*70)

    try:
        df_quality = batch_quality_check(raw_images_path, quality_report_path)

        if df_quality is None:
            print("❌ Quality check failed. Please review your images.")
            return

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
            print("Continuing with processing (failed images will be skipped).")

    except Exception as e:
        print(f"❌ Error during quality assessment: {e}")
        return

    # ====================================================================
    # PHASE 2: FLOWCHART PIPELINE – per-image loop
    #   Convert to 8-bit → Crop regions → Denoise/resize → OCR → store
    # ====================================================================
    print("\n" + "="*70)
    print("PHASE 2: IMAGE PREPROCESSING & PARAMETER EXTRACTION")
    print("="*70)

    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
    raw_files = []
    for ext in image_extensions:
        raw_files.extend(Path(raw_images_path).glob(f'*{ext}'))
        raw_files.extend(Path(raw_images_path).glob(f'*{ext.upper()}'))

    cropper = RegionCropper()
    extractor = ParameterExtractor(ocr_engine='tesseract')

    # Storage lists (one entry per image, matching the flowchart)
    all_parameters = []

    for img_path in raw_files:
        print(f"\nProcessing: {img_path.name}")

        # Step 1 – Convert to 8-bit / preprocess (saves to processed/)
        processor = ImageProcessor(str(img_path))
        if not processor.load_image():
            all_parameters.append(extractor._get_empty_parameters(img_path.name))
            continue

        preprocessed = processor.preprocess_for_ocr()
        if preprocessed is not None:
            out_path = Path(processed_images_path) / img_path.name
            processor.save_processed_image(str(out_path))

        # Step 2 – Crop parameter regions
        crops = cropper.crop_parameter_regions(processor.original_image)

        if crops:
            # Steps 3–5 – Denoise/resize each sub-image, OCR, store
            params = extractor.extract_from_cropped_regions(str(img_path))
        else:
            # Fallback: full-image regex OCR
            processed_path = Path(processed_images_path) / img_path.name
            src_path = str(processed_path) if processed_path.exists() else str(img_path)
            params = extractor.extract_from_image(src_path)
            params['image_file'] = img_path.name

        all_parameters.append(params)

    if not all_parameters:
        print("❌ No parameters extracted.")
        return

    # Persist extracted parameters to CSV
    column_order = [
        'image_file', 'fluoro_time', 'total_fluoro_kair',
        'dose_entree_peau_max', 'exposit_ni', 'total_pds',
        'total_dose', 'frequence_acquisition',
    ]
    df = pd.DataFrame(all_parameters)
    for col in column_order:
        if col not in df.columns:
            df[col] = None
    df = df[[c for c in column_order if c in df.columns]]
    df.to_csv(extracted_data_path, index=False)
    print(f"\n✓ Extracted parameters from {len(df)} images")
    print(f"✓ Results saved to: {extracted_data_path}")

    # ====================================================================
    # PHASE 3: STATISTICAL ANALYSIS – quartiles, histograms, Excel
    # ====================================================================
    print("\n" + "="*70)
    print("PHASE 3: STATISTICAL ANALYSIS & DRL CALCULATION")
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

        # Save DRLs (CSV)
        analyzer.save_drls(drls_output_path)

        # Generate box-plot visualizations
        print("\nGenerating box-plot visualizations...")
        analyzer.visualize_distributions(visualizations_path)
        print(f"✓ Box plots saved to {visualizations_path}")

        # Generate histograms with quartile lines
        print("Generating histograms...")
        analyzer.generate_histograms(visualizations_path)

        # Export full Excel report (raw data + stats + histograms)
        print("Exporting Excel report...")
        analyzer.generate_full_report(excel_output_path)

    except Exception as e:
        print(f"❌ Error during statistical analysis: {e}")
        return

    # ====================================================================
    # PIPELINE COMPLETE
    # ====================================================================
    print("\n" + "="*70)
    print("✓ PIPELINE COMPLETE!")
    print("="*70)
    print("\nResults saved to:")
    print(f"  - Quality report:        {quality_report_path}")
    print(f"  - Extracted parameters:  {extracted_data_path}")
    print(f"  - DRLs (CSV):            {drls_output_path}")
    print(f"  - Full report (Excel):   {excel_output_path}")
    print(f"  - Visualizations:        {visualizations_path}")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
