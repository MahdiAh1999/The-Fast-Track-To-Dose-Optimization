# First PhD Project: Automated DRL Establishment for Interventional Radiology

## 📋 Project Overview

This project establishes Diagnostic Reference Levels (DRLs) for interventional radiology and radioguided surgery using automated image analysis and statistical methods.

## 🎯 Objectives

1. **Automated Parameter Extraction**: Analyze dosimetric result images from ~30 interventions and extract key parameters
2. **Statistical Analysis**: Calculate local DRLs as the 3rd quartile (75th percentile) of the collected data
3. **Validation**: Compare automated extraction methodology with manual extraction to assess efficiency

## 📊 Dosimetric Parameters

The following parameters are extracted from each intervention: 
- Fluoro time
- Total fluoro Kair
- Dose entrée peau max
- Exposit NI
- Total PDS
- Total dose
- Fréquence acquisition (F/S)

## 🛠️ Technology Stack

- **Image Processing**: OpenCV, Tesseract OCR / EasyOCR
- **Data Analysis**: Python, Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn
- **Quality Assurance**: Custom image quality validation

## 🔄 Methodology

### Phase 1: Image Quality Assessment ⭐ NEW
Before processing, all raw images undergo quality validation to ensure accurate OCR results:
- **Resolution check**: Minimum 800x600 pixels
- **Brightness analysis**: Optimal range for OCR
- **Contrast evaluation**: Sufficient text-background separation
- **Sharpness assessment**: Detection of blurry images
- **Quality report generation**: Pass/Warning/Fail status for each image

Images failing quality checks are flagged for manual review or re-capture.

### Phase 2: Image Preprocessing
- Grayscale conversion
- Adaptive thresholding
- Noise reduction
- Image enhancement

### Phase 3: Parameter Extraction
- OCR text extraction (Tesseract/EasyOCR)
- Pattern matching for dosimetric parameters
- Data validation and cleaning

### Phase 4: Statistical Analysis
- Calculate DRLs as 3rd quartile (75th percentile)
- Descriptive statistics
- Distribution analysis

### Phase 5: Validation
- Compare automated vs manual extraction
- Accuracy assessment
- Efficiency analysis

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
│   ├── image_quality_checker.py    # ⭐ NEW: Quality validation
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

### Prerequisites
- Python 3.8+
- Tesseract OCR installed on your system
  - Windows: [Download from GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Mac: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

### Installation

1. Clone the repository:
```bash
git clone https://github.com/MahdiAh1999/FIRST-PHD-PROJECT.git
cd FIRST-PHD-PROJECT
```

2. Create and activate virtual environment:
```bash
python -m venv v
# Windows
v\Scripts\activate
# Mac/Linux
source v/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Place your dosimetric images in `data/raw/`

### Usage

**Step 1: Quality Check** ⭐ NEW
```python
from src.image_quality_checker import batch_quality_check

# Check all images before processing
batch_quality_check('data/raw/', 'data/quality_reports/quality_report.csv')
```

**Step 2: Process Images**
```python
from src.image_processor import batch_preprocess_images

batch_preprocess_images('data/raw/', 'data/processed/')
```

**Step 3: Extract Parameters**
```python
from src.parameter_extractor import ParameterExtractor

extractor = ParameterExtractor(ocr_engine='tesseract')
results = extractor.batch_extract('data/processed/', 'results/extracted_parameters.csv')
```

**Step 4: Calculate DRLs**
```python
from src.statistical_analyzer import StatisticalAnalyzer

analyzer = StatisticalAnalyzer('results/extracted_parameters.csv')
analyzer.load_data()
drls = analyzer.calculate_drls()
analyzer.save_drls('results/drls/local_drls.csv')
```

## 📊 Workflow

### Step 1: Quality Assessment
- Upload raw dosimetric images to `data/raw/`
- Run quality validation to identify problematic images
- Review flagged images and decide on actions (re-capture or manual processing)

### Step 2: Image Processing
- Preprocess images that passed quality checks
- Apply OCR-optimized transformations
- Save processed images for extraction

### Step 3: Parameter Extraction
- Use OCR to extract text from processed images
- Parse dosimetric parameters using regex patterns
- Validate and save extracted data

### Step 4: Statistical Analysis
- Load extracted parameters
- Calculate descriptive statistics
- Compute DRLs as 3rd quartile (75th percentile)
- Generate visualizations

### Step 5: Validation
- Compare automated extraction with manual results
- Calculate accuracy metrics
- Assess time efficiency improvements

## 🎓 Research Context

This project is part of doctoral research in medical physics, focusing on radiation dose optimization in interventional radiology. DRLs serve as investigation levels to identify and reduce unnecessarily high radiation doses while maintaining diagnostic quality.

## 📝 License

This project is part of PhD research.

## 👤 Author

**Mahdi Ahabchane**
- GitHub: [@MahdiAh1999](https://github.com/MahdiAh1999)

## 🙏 Acknowledgments

- Interventional radiology department for providing dosimetric data
- Research supervisors and collaborators
- Open-source OCR community (Tesseract, EasyOCR)
