# First PhD Project: Automated DRL Establishment for Interventional Radiology

[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen)](https://github.com/MahdiAh1999/FIRST-PHD-PROJECT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-PhD%20Research-lightgrey.svg)](LICENSE)

## 📋 Project Overview

This project establishes Diagnostic Reference Levels (DRLs) for interventional radiology and radioguided surgery using automated image analysis and statistical methods. It leverages Python-based OCR to solve the manual extraction bottleneck in dose optimization.

> **Research Poster Results**: 
> - 🚀 **80% Faster** than manual PACS extraction.
> - ✅ **99.43% Accuracy** across 350 extracted values.
> - ⚡ **Real-time DRL computation** from PACS dose reports.

## 🎯 Objectives

1. **Automated Parameter Extraction**: Capture dose metrics (PKA, Ka,r, fluoroscopy time) from PACS images automatically.
2. **Statistical Analysis**: Compute DRL statistics (median, 3rd quartile) across procedure types.
3. **Validation**: Demonstrate accuracy and time reduction vs manual extraction.
4. **Seamless Implementation**: Deploy into radiology workflows without PACS modification.

## 📊 Key Results (Coronary Angiography, n=50)

| Metric | Value (Q3) |
| :--- | :--- |
| **PKA** | 4,823 µGy·m² |
| **Ka,r** | 2,570 µGy·m² |
| **Fluoro Time (FT)** | 7.0 min |

- **Extraction Accuracy**: 99.43% (348/350 correct).
- **Time Savings**: 80% reduction compared to manual entry.
- **Cross-System Validation**: Reproducible across Siemens Artis Q and Philips Azurion platforms.

## 🛠️ Technology Stack

- **Algorithm**: Python 3.8 + OpenCV + Tesseract OCR / EasyOCR
- **Data Analysis**: Pandas, NumPy, SciPy (SEM, SRMR, RMSEA, CFI, TLI)
- **Visualization**: Matplotlib, Seaborn
- **Quality Assurance**: Custom automated range-checking and image quality validation

## 🔄 Detailed Methodology

### Phase 1: Image Quality Assessment
Before processing, raw images undergo quality validation (Resolution, Brightness, Contrast, Sharpness).
- **Limitation**: 2 errors (0.57%) produced wrong values due to range-checking safeguards.

### Phase 2: Image Preprocessing & OCR Pipeline
1. **Extract**: Capture raw dose reports from PACS.
2. **Calculate**: Compute DRL statistics (Median, 3rd Quartile).
3. **Validate**: 99.43% accuracy validation.
4. **Implement**: Seamless workflow integration.

### Phase 3: Statistical Analysis
- Calculate DRLs as 3rd quartile (75th percentile).
- **Statistics**: χ²[201]=566.88, p<.0001; SRMR=.12, RMSEA=.08, CFI=.88, TLI=.863.

## 📁 Project Structure

```
first-PHD-project/
├── data/
│   ├── raw/              # Original dosimetric screenshots
│   ├── processed/        # Preprocessed images
│   ├── manual/           # Manual extraction results for comparison
│   └── quality_reports/  # Image quality assessment reports
├── notebooks/
│   ├── 01_image_analysis.ipynb
│   ├── 02_statistical_analysis.ipynb
│   └── 03_comparison_validation.ipynb
├── src/
│   ├── image_quality_checker.py
│   ├── image_processor.py
│   ├── parameter_extractor.py
│   └── statistical_analyzer.py
├── results/
│   ├── drls/             # Final DRL values
│   └── visualizations/   # Charts and graphs
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

Check the [Algorithm Details & Wiki](https://MahdiAh1999.github.io/FIRST-PHD-PROJECT/) for in-depth documentation on the OCR pipeline.

## 👤 Author

**Mahdi Ahabchane**
- LPHE-MS, Mohammed V University, Rabat
- GitHub: [@MahdiAh1999](https://github.com/MahdiAh1999)

## 🙏 Acknowledgments

- UM6P Hospitals & Mohammed V University
- Dr. Anass Chehboun & Pr. Rajae Sebihi
- Open-source OCR community
