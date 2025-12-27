# First PhD Project:  Automated DRL Establishment for Interventional Radiology

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

- **Image Processing**:  Tesseract OCR / EasyOCR
- **Data Analysis**: Python, Pandas, NumPy
- **Visualization**: Matplotlib, Seaborn

## 📁 Project Structure

```
first-PHD-project/
├── data/
│   ├── raw/              # Original dosimetric screenshots
│   ├── processed/        # Extracted data (CSV format)
│   └── manual/           # Manual extraction results for comparison
├── notebooks/
│   ├── 01_image_analysis.ipynb
│   ├── 02_statistical_analysis.ipynb
│   └── 03_comparison_validation.ipynb
├── src/
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
- pip package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/MahdiAh1999/first-PHD-project.git
cd first-PHD-project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Tesseract OCR (system dependency)
# On Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
```

### Usage

1. Place your dosimetric screenshots in `data/raw/`
2. Run the notebooks in order:
   - `01_image_analysis.ipynb`: Extract parameters from images
   - `02_statistical_analysis.ipynb`: Calculate DRLs
   - `03_comparison_validation.ipynb`: Compare with manual method

## 📈 Methodology

### Step 1: Image Analysis
- Load dosimetric screenshots
- Apply OCR to extract text
- Parse and structure dosimetric parameters
- Save to CSV format

### Step 2: Statistical Analysis
- Load extracted parameters
- Calculate descriptive statistics
- Compute 3rd quartile (75th percentile) for each parameter
- Generate DRL values

### Step 3: Validation
- Compare automated vs. manual extraction
- Assess accuracy, precision, and efficiency
- Visualize comparison results

## 📝 License

This project is part of PhD research. 

## 👤 Author

**Mahdi Ah**
- GitHub: [@MahdiAh1999](https://github.com/MahdiAh1999)

## 🙏 Acknowledgments

- Interventional radiology department for providing dosimetric data
- Research supervisors and collaborators