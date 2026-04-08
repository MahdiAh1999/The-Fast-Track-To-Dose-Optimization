# The Fast Track To Dose Optimization: Python OCR For Real-time DRLs In Interventional Radiology & Radioguided Surgery

[![Open Source](https://img.shields.io/badge/Open%20Source-%E2%9D%A4-brightgreen)](https://github.com/MahdiAh1999/FIRST-PHD-PROJECT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

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

## 👥 Population & System

- **Study population**: n=50 interventional radiology patients
- **Procedure**: Coronary angiography
- **Primary system**: Siemens Artis Q angiography system
- **Cross-validation system**: Philips Azurion
- **Reference**: Tsuris & Dendalts (2023)

## 📊 Key Results (Coronary Angiography, n=50)

| Metric | Q1 | Q3 (DRL) |
| :--- | :--- | :--- |
| **PKA** | — | 4,823 µGy·m² |
| **Ka,r** | — | 2,570 µGy |
| **Fluoro Time (FT)** | — | 7.0 min |

- **Extraction Accuracy**: 99.43% (348/350 correct).
- **Time Savings**: 80% reduction compared to manual entry.
- **Cross-System Validation**: Reproducible across Siemens Artis Q and Philips Azurion platforms.

## 📐 Statistical Model

Structural equation model goodness-of-fit indices:

> χ²[201]=566.88, p<.0001; SRMR=.12, RMSEA=.08, CFI=.88, TLI=.863

## 🛠️ Technology Stack

- **Algorithm**: Python 3.8 + OpenCV + Tesseract OCR / EasyOCR
- **Data Analysis**: Pandas, NumPy, SciPy (SEM, SRMR, RMSEA, CFI, TLI)
- **Visualization**: Matplotlib, Seaborn
- **Quality Assurance**: Custom automated range-checking and image quality validation

## 🗒 Detailed Methodology

### Step 1 — EXTRACT: Automated PACS Image Capture
Raw dosimetric images are captured from PACS and undergo:
- Resolution, brightness, contrast, and sharpness quality assessment.
- Adaptive preprocessing (denoising, thresholding) before OCR.
- Tesseract / EasyOCR extraction with French + English language support.

### Step 2 — CALCULATE: DRL Statistical Computation (Q3/75th percentile)
- Compute descriptive statistics (mean, median, SD, Q1, Q3) per parameter.
- Establish DRLs as the **3rd quartile (75th percentile)** of the distribution.
- Primary DRL parameters: **PKA** (µGy·m²), **Ka,r** (µGy), **Fluoro Time** (min).

### Step 3 — VALIDATE: 99.43% Accuracy Cross-validation
- Automated results cross-validated against manual PACS extraction.
- **Accuracy**: 99.43% (348/350 values correct across 7 variables).
- Cross-system reproducibility confirmed on Siemens Artis Q and Philips Azurion.
- Structural model fit assessed: χ²[201]=566.88, p<.0001; SRMR=.12, RMSEA=.08, CFI=.88, TLI=.863.

### Step 4 — IMPLEMENT: Seamless Workflow Integration
- No PACS modification required; works from screenshot exports.
- **80% time reduction** vs manual extraction (3.75 min/image → seconds).
- Outputs local DRL CSV files ready for clinical reporting.

## ⚠ Limitations

- 2 values (0.57%) were flagged by the range-checking post-processing safeguard and set to `None` during extraction. These represent values outside the clinically expected range and do not affect the overall DRL computation.

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
│   ├── statistical_analyzer.py
│   ├── comparison_validator.py
│   └── data_validator.py
├── results/
│   ├── drls/             # Final DRL values
│   └── visualizations/   # Charts and graphs
├── requirements.txt
└── README.md
```

## 🚀 Getting Started

People wanting to know more details about the open-source algorithm can find the documentation here:
**[Algorithm Details & Open Source Wiki](https://MahdiAh1999.github.io/FIRST-PHD-PROJECT/)**

## 👤 Author

**Mahdi Ahabchane**
- LPHE-MS, Mohammed V University, Rabat
- GitHub: [@MahdiAh1999](https://github.com/MahdiAh1999)

## 🙏 Acknowledgments

- UM6P Hospitals & Mohammed V University
- Dr. Anass Chehboun & Pr. Rajae Sebihi
- Open-source OCR community