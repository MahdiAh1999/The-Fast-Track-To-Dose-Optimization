# Manual Data Entry Guide

## Purpose
This folder contains manually extracted dosimetric parameters for comparison with automated extraction results.

## Instructions

### Step 1: Create Your Manual Extraction File
1. Copy `manual_extraction_template.csv` and rename it (e.g., `manual_extraction_batch1.csv`)
2. Keep the same column headers

### Step 2: Fill in the Data
For each dosimetric image in `data/raw/`, manually read and record:

- **image_file**: Exact filename (e.g., `image_001.png`)
- **fluoro_time**: Fluoroscopy time (in minutes or seconds - document unit)
- **total_fluoro_kair**: Total fluoroscopy Kerma-air product
- **dose_entree_peau_max**: Maximum entrance skin dose
- **exposit_ni**: Exposure NI value
- **total_pds**: Total PDS (Dose Area Product)
- **total_dose**: Total radiation dose
- **frequence_acquisition**: Acquisition frequency (F/S - Frames per second)
- **operator_name**: Your name or ID
- **extraction_date**: Date of manual extraction (YYYY-MM-DD)
- **notes**: Any observations or issues with the image

### Step 3: Quality Guidelines
- Record values exactly as displayed in the image
- If a parameter is not visible or unclear, leave the cell empty
- Document any unusual cases in the notes column
- Use consistent decimal separators (prefer dots over commas)
- Save the file with UTF-8 encoding

### Step 4: File Naming Convention
Use descriptive names:
- `manual_extraction_batch1.csv` - First batch of images
- `manual_extraction_operator1.csv` - By specific operator
- `manual_extraction_YYYYMMDD.csv` - By date

### Example Entry
```csv
image_file,fluoro_time,total_fluoro_kair,dose_entree_peau_max,exposit_ni,total_pds,total_dose,frequence_acquisition,operator_name,extraction_date,notes
dose_screen_001.png,15.2,125.5,850.3,42,1250,980.5,7.5,Dr. Smith,2026-01-20,Clear image
dose_screen_002.png,8.5,85.2,520.1,28,890,645.2,7.5,Dr. Smith,2026-01-20,Slightly blurry
dose_screen_003.png,12.0,,750.0,35,1100,820.0,7.5,Dr. Smith,2026-01-20,Kair value not visible
```

## Validation Tips
- Double-check each value before moving to the next image
- Have a second person verify critical values if possible
- Take breaks to avoid fatigue-related errors
- Compare your extraction time with automated extraction later

## Files in This Folder
- `manual_extraction_template.csv` - Empty template (DO NOT MODIFY)
- Your manual extraction files (e.g., `manual_extraction_batch1.csv`)

## Next Steps
Once manual extraction is complete, use the validation notebook (`03_comparison_validation.ipynb`) to compare manual vs automated results.
