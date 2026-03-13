# The Fast Track To Dose Optimization: Python OCR For Real-time DRLs In Interventional Radiology \u0026 Radioguided Surgery

[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen)](https://github.com/MahdiAh1999/FIRST-PHD-PROJECT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 📋 Project Overview

This project establishes Diagnostic Reference Levels (DRLs) for interventional radiology and radioguided surgery using automated image analysis and statistical methods. It leverages Python-based OCR to solve the manual extraction bottleneck in dose optimization.

\u003e **Research Poster Results**: 
\u003e - \ud83d\ude80 **80% Faster** than manual PACS extraction.
\u003e - \u2705 **99.43% Accuracy** across 350 extracted values.
\u003e - \u26a1 **Real-time DRL computation** from PACS dose reports.

## \ud83c\udfaf Objectives

1. **Automated Parameter Extraction**: Capture dose metrics (PKA, Ka,r, fluoroscopy time) from PACS images automatically.
2. **Statistical Analysis**: Compute DRL statistics (median, 3rd quartile) across procedure types.
3. **Validation**: Demonstrate accuracy and time reduction vs manual extraction.
4. **Seamless Implementation**: Deploy into radiology workflows without PACS modification.

## \ud83d\udcca Key Results (Coronary Angiography, n=50)

| Metric | Value (Q3) |
| :--- | :--- |
| **PKA** | 4,823 \u00b5Gy\u00b7m\u00b2 |
| **Ka,r** | 2,570 \u00b5Gy\u00b7m\u00b2 |
| **Fluoro Time (FT)** | 7.0 min |

- **Extraction Accuracy**: 99.43% (348/350 correct).
- **Time Savings**: 80% reduction compared to manual entry.
- **Cross-System Validation**: Reproducible across Siemens Artis Q and Philips Azurion platforms.

## \ud83d\udee0\ufe0f Technology Stack

- **Algorithm**: Python 3.8 + OpenCV + Tesseract OCR / EasyOCR
- **Data Analysis**: Pandas, NumPy, SciPy (SEM, SRMR, RMSEA, CFI, TLI)
- **Visualization**: Matplotlib, Seaborn
- **Quality Assurance**: Custom automated range-checking and image quality validation

## \ud83d\uddd4 Detailed Methodology

### Phase 1: Image Quality Assessment
Before processing, raw images undergo quality validation (Resolution, Brightness, Contrast, Sharpness).
- **Limitation**: 2 errors (0.57%) produced wrong values due to range-checking safeguards.

### Phase 2: Image Preprocessing \u0026 OCR Pipeline
1. **Extract**: Capture raw dose reports from PACS.
2. **Calculate**: Compute DRL statistics (Median, 3rd Quartile).
3. **Validate**: 99.43% accuracy validation.
4. **Implement**: Seamless workflow integration.

### Phase 3: Statistical Analysis
- Calculate DRLs as 3rd quartile (75th percentile).
- **Statistics**: \u03c7\u00b2[201]=566.88, p\u003c.0001; SRMR=.12, RMSEA=.08, CFI=.88, TLI=.863.

## \ud83d\udcc1 Project Structure

```
first-PHD-project/
\u251c\u2500\u2500 data/
\u2502   \u251c\u2500\u2500 raw/              # Original dosimetric screenshots
\u2502   \u251c\u2500\u2500 processed/        # Preprocessed images
\u2502   \u251c\u2500\u2500 manual/           # Manual extraction results for comparison
\u2502   \u2514\u2500\u2500 quality_reports/  # Image quality assessment reports
\u251c\u2500\u2500 notebooks/
\u2502   \u251c\u2500\u2500 01_image_analysis.ipynb
\u2502   \u251c\u2500\u2500 02_statistical_analysis.ipynb
\u2502   \u2514\u2500\u2500 03_comparison_validation.ipynb
\u251c\u2500\u2500 src/
\u2502   \u251c\u2500\u2500 image_quality_checker.py
\u2502   \u251c\u2500\u2500 image_processor.py
\u2502   \u251c\u2500\u2500 parameter_extractor.py
\u2502   \u2514\u2500\u2500 statistical_analyzer.py
\u251c\u2500\u2500 results/
\u2502   \u251c\u2500\u2500 drls/             # Final DRL values
\u2502   \u2514\u2500\u2500 visualizations/   # Charts and graphs
\u251c\u2500\u2500 requirements.txt
\u2514\u2500\u2500 README.md
```

## \ud83d\ude80 Getting Started

People wanting to know more details about the open-source algorithm can find the documentation here:
**[Algorithm Details \u0026 Open Source Wiki](https://MahdiAh1999.github.io/FIRST-PHD-PROJECT/)**

## \ud83d\udc64 Author

**Mahdi Ahabchane**
- LPHE-MS, Mohammed V University, Rabat
- GitHub: [@MahdiAh1999](https://github.com/MahdiAh1999)

## \ud83d\ude4f Acknowledgments

- UM6P Hospitals \u0026 Mohammed V University
- Dr. Anass Chehboun \u0026 Pr. Rajae Sebihi
- Open-source OCR community