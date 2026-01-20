# Jupyter Notebooks

This directory contains three Jupyter notebooks for the complete DRL establishment workflow.

## 📓 Notebook 01: Image Analysis and Parameter Extraction

**Purpose**: Process dosimetric images and extract parameters using OCR

**Workflow**:
1. **Import Libraries**: Load all necessary modules
2. **Quality Assessment**: 
   - Run `batch_quality_check()` on raw images
   - Review quality report
   - Identify problematic images
3. **Image Preprocessing**:
   - Load sample image
   - Apply preprocessing (grayscale, thresholding, denoising)
   - Display before/after comparison
   - Batch process all images
4. **Parameter Extraction**:
   - Initialize ParameterExtractor
   - Test on single image
   - Show extracted text and parsed parameters
   - Batch extract from all processed images
   - Save to CSV
5. **Data Validation**:
   - Load extracted data
   - Check for missing values
   - Detect outliers
   - Generate validation report

**Key Outputs**:
- `data/quality_reports/quality_report.csv`
- `data/processed/` (preprocessed images)
- `results/extracted_parameters.csv`

---

## 📊 Notebook 02: Statistical Analysis and DRL Calculation

**Purpose**: Calculate Diagnostic Reference Levels from extracted data

**Workflow**:
1. **Load Extracted Data**: Read CSV from Notebook 01
2. **Data Exploration**:
   - Display first rows
   - Check data types
   - Summary statistics
3. **Descriptive Statistics**:
   - Mean, median, std dev for each parameter
   - Quartiles (Q1, Q2, Q3)
   - Min/max values
4. **DRL Calculation**:
   - Calculate 75th percentile for each parameter
   - Create DRL summary table
   - Save to CSV
5. **Visualizations**:
   - Box plots for each parameter
   - Highlight DRL lines
   - Distribution histograms
   - Save plots to results/visualizations/
6. **Statistical Tests**:
   - Normality tests
   - Confidence intervals for DRLs

**Key Outputs**:
- `results/drls/local_drls.csv`
- `results/visualizations/parameter_distributions.png`
- Statistical summary tables

---

## ✅ Notebook 03: Comparison and Validation

**Purpose**: Compare automated extraction with manual extraction

**Workflow**:
1. **Load Both Datasets**:
   - Automated extraction CSV
   - Manual extraction Excel/CSV
2. **Merge Datasets**: Match by image filename
3. **Calculate Accuracy Metrics**:
   - Mean Absolute Error (MAE)
   - Mean Absolute Percentage Error (MAPE)
   - Root Mean Square Error (RMSE)
   - Pearson correlation
   - Agreement within 5%, 10%
4. **Bland-Altman Analysis**:
   - Plot differences vs means
   - Calculate bias and limits of agreement
   - Generate plots for each parameter
5. **Correlation Analysis**:
   - Scatter plots: Manual vs Automated
   - Perfect agreement line
   - Correlation coefficients
6. **Time Efficiency Analysis**:
   - Compare extraction time
   - Calculate time savings
7. **Generate Validation Report**:
   - Summary of accuracy metrics
   - Recommendations for improvement

**Key Outputs**:
- `results/comparison_metrics.csv`
- `results/visualizations/correlation_plots.png`
- `results/visualizations/bland_altman_*.png`
- Validation report

---

## 🚀 Quick Start

### Run All Notebooks in Sequence:

```bash
# Activate virtual environment
v\Scripts\activate  # Windows
# source v/bin/activate  # Mac/Linux

# Start Jupyter Lab
jupyter lab
```

### Or Run from Command Line:

```bash
# Convert notebooks to HTML reports
jupyter nbconvert --to html notebooks/*.ipynb

# Execute notebooks programmatically
jupyter nbconvert --to notebook --execute notebooks/01_image_analysis.ipynb
```

---

## 📋 Prerequisites

1. **Data Preparation**:
   - Place raw images in `data/raw/`
   - Ensure manual extraction file is in `data/manual/`

2. **Environment Setup**:
   - Python 3.8+
   - All packages from `requirements.txt` installed
   - Tesseract OCR installed on system

3. **Configuration**:
   - Review and adjust `config.json` if needed
   - Set OCR language and quality thresholds

---

## 💡 Tips

- **Run cells sequentially**: Each notebook builds on previous steps
- **Check outputs**: Verify CSV files are created after each notebook
- **Adjust parameters**: Modify OCR settings in config.json if extraction quality is poor
- **Save often**: Notebooks autosave, but manually save important results
- **Clear outputs**: Use "Cell > All Output > Clear" before committing to Git

---

## 🔍 Troubleshooting

**Issue**: OCR returns no text
- **Solution**: Check image quality, ensure proper preprocessing, verify Tesseract installation

**Issue**: Low extraction accuracy
- **Solution**: Adjust regex patterns in config.json, improve image quality

**Issue**: Missing values in results
- **Solution**: Review data validation report, manually verify problem images

**Issue**: Notebooks won't run
- **Solution**: Verify virtual environment is activated, check all dependencies installed
