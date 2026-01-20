"""
Data Validator Module
Validate extracted parameters, handle missing values, and detect outliers
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json
from src.config_manager import config


class DataValidator:
    """Validate and clean extracted dosimetric parameters"""
    
    def __init__(self, data_path: str = None, df: pd.DataFrame = None):
        """
        Initialize validator
        
        Args:
            data_path (str): Path to CSV with extracted parameters
            df (pd.DataFrame): DataFrame to validate (alternative to data_path)
        """
        self.data_path = data_path
        self.df = df
        self.validation_report = {}
        
        if data_path and df is None:
            self.load_data()
    
    def load_data(self) -> bool:
        """Load data from CSV"""
        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✓ Loaded {len(self.df)} records from {self.data_path}")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def check_missing_values(self) -> Dict[str, any]:
        """
        Check for missing values in the dataset
        
        Returns:
            dict: Missing value statistics
        """
        if self.df is None:
            return {"error": "No data loaded"}
        
        # Select numeric columns (exclude image_file)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        missing_stats = {}
        for col in numeric_cols:
            missing_count = self.df[col].isna().sum()
            missing_pct = (missing_count / len(self.df)) * 100
            missing_stats[col] = {
                'count': int(missing_count),
                'percentage': round(missing_pct, 2),
                'status': 'ok' if missing_pct < 20 else 'warning' if missing_pct < 50 else 'critical'
            }
        
        return missing_stats
    
    def detect_outliers(self, method: str = 'zscore', threshold: float = 3.0) -> Dict[str, List[int]]:
        """
        Detect outliers using Z-score or IQR method
        
        Args:
            method (str): 'zscore' or 'iqr'
            threshold (float): Z-score threshold or IQR multiplier
            
        Returns:
            dict: Outlier indices for each parameter
        """
        if self.df is None:
            return {"error": "No data loaded"}
        
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        outliers = {}
        
        for col in numeric_cols:
            data = self.df[col].dropna()
            
            if len(data) == 0:
                outliers[col] = []
                continue
            
            if method == 'zscore':
                z_scores = np.abs((data - data.mean()) / data.std())
                outlier_indices = data.index[z_scores > threshold].tolist()
            
            elif method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                outlier_indices = data.index[(data < lower_bound) | (data > upper_bound)].tolist()
            
            else:
                raise ValueError(f"Unknown method: {method}. Use 'zscore' or 'iqr'")
            
            outliers[col] = outlier_indices
        
        return outliers
    
    def check_value_ranges(self, expected_ranges: Dict[str, Tuple[float, float]] = None) -> Dict[str, any]:
        """
        Check if values are within expected ranges
        
        Args:
            expected_ranges (dict): Dictionary of parameter: (min, max) tuples
            
        Returns:
            dict: Out-of-range statistics
        """
        if self.df is None:
            return {"error": "No data loaded"}
        
        # Default expected ranges (can be customized)
        if expected_ranges is None:
            expected_ranges = {
                'fluoro_time': (0, 120),  # 0-120 minutes
                'total_fluoro_kair': (0, 10000),  # mGy
                'dose_entree_peau_max': (0, 10000),  # mGy
                'exposit_ni': (0, 500),
                'total_pds': (0, 50000),  # cGy.cm²
                'total_dose': (0, 10000),  # mGy
                'frequence_acquisition': (0, 30)  # frames/second
            }
        
        out_of_range = {}
        
        for param, (min_val, max_val) in expected_ranges.items():
            if param not in self.df.columns:
                continue
            
            data = self.df[param].dropna()
            below_min = data[data < min_val]
            above_max = data[data > max_val]
            
            out_of_range[param] = {
                'below_min': len(below_min),
                'above_max': len(above_max),
                'below_min_indices': below_min.index.tolist(),
                'above_max_indices': above_max.index.tolist(),
                'status': 'ok' if len(below_min) == 0 and len(above_max) == 0 else 'warning'
            }
        
        return out_of_range
    
    def validate_data_types(self) -> Dict[str, bool]:
        """Check if columns have correct data types"""
        if self.df is None:
            return {"error": "No data loaded"}
        
        expected_types = {
            'image_file': 'object',
            'fluoro_time': 'numeric',
            'total_fluoro_kair': 'numeric',
            'dose_entree_peau_max': 'numeric',
            'exposit_ni': 'numeric',
            'total_pds': 'numeric',
            'total_dose': 'numeric',
            'frequence_acquisition': 'numeric'
        }
        
        type_validation = {}
        
        for col, expected_type in expected_types.items():
            if col not in self.df.columns:
                type_validation[col] = {'status': 'missing', 'expected': expected_type}
                continue
            
            actual_type = self.df[col].dtype
            
            if expected_type == 'numeric':
                is_valid = pd.api.types.is_numeric_dtype(actual_type)
            elif expected_type == 'object':
                is_valid = actual_type == 'object'
            else:
                is_valid = str(actual_type) == expected_type
            
            type_validation[col] = {
                'status': 'valid' if is_valid else 'invalid',
                'expected': expected_type,
                'actual': str(actual_type)
            }
        
        return type_validation
    
    def run_full_validation(self) -> Dict[str, any]:
        """
        Run all validation checks
        
        Returns:
            dict: Complete validation report
        """
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return {}
        
        print("\n" + "="*70)
        print("RUNNING DATA VALIDATION")
        print("="*70)
        
        # 1. Missing values
        print("\n1. Checking for missing values...")
        missing_stats = self.check_missing_values()
        
        # 2. Data types
        print("2. Validating data types...")
        type_validation = self.validate_data_types()
        
        # 3. Outliers
        print("3. Detecting outliers (Z-score method)...")
        outliers_zscore = self.detect_outliers(method='zscore', threshold=3.0)
        
        print("4. Detecting outliers (IQR method)...")
        outliers_iqr = self.detect_outliers(method='iqr', threshold=1.5)
        
        # 4. Value ranges
        print("5. Checking value ranges...")
        range_check = self.check_value_ranges()
        
        # Compile report
        self.validation_report = {
            'total_records': len(self.df),
            'missing_values': missing_stats,
            'data_types': type_validation,
            'outliers_zscore': outliers_zscore,
            'outliers_iqr': outliers_iqr,
            'value_ranges': range_check
        }
        
        self._print_validation_summary()
        
        return self.validation_report
    
    def _print_validation_summary(self):
        """Print validation summary"""
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)
        
        # Missing values summary
        print("\n📊 MISSING VALUES:")
        missing = self.validation_report['missing_values']
        critical_missing = [k for k, v in missing.items() if v['status'] == 'critical']
        warning_missing = [k for k, v in missing.items() if v['status'] == 'warning']
        
        if critical_missing:
            print(f"  ❌ Critical (>50% missing): {', '.join(critical_missing)}")
        if warning_missing:
            print(f"  ⚠ Warning (20-50% missing): {', '.join(warning_missing)}")
        if not critical_missing and not warning_missing:
            print("  ✓ No significant missing values")
        
        # Outliers summary
        print("\n🔍 OUTLIERS (Z-score method):")
        outliers_z = self.validation_report['outliers_zscore']
        total_outliers_z = sum(len(v) for v in outliers_z.values() if isinstance(v, list))
        if total_outliers_z > 0:
            print(f"  ⚠ Found {total_outliers_z} potential outliers across all parameters")
            for param, indices in outliers_z.items():
                if len(indices) > 0:
                    print(f"    - {param}: {len(indices)} outliers")
        else:
            print("  ✓ No significant outliers detected")
        
        # Range check summary
        print("\n📏 VALUE RANGE CHECKS:")
        ranges = self.validation_report['value_ranges']
        issues = [k for k, v in ranges.items() if v['status'] == 'warning']
        if issues:
            print(f"  ⚠ Parameters with out-of-range values: {', '.join(issues)}")
        else:
            print("  ✓ All values within expected ranges")
        
        print("\n" + "="*70 + "\n")
    
    def save_report(self, output_path: str):
        """Save validation report to JSON"""
        if not self.validation_report:
            print("No validation report available. Run run_full_validation() first.")
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.validation_report, f, indent=2)
            print(f"✓ Validation report saved to: {output_path}")
            return True
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False
    
    def get_clean_data(self, remove_outliers: bool = False, fill_missing: bool = False) -> pd.DataFrame:
        """
        Return cleaned version of the data
        
        Args:
            remove_outliers (bool): Remove outlier rows
            fill_missing (bool): Fill missing values with median
            
        Returns:
            pd.DataFrame: Cleaned data
        """
        if self.df is None:
            print("No data loaded.")
            return None
        
        df_clean = self.df.copy()
        
        if remove_outliers and 'outliers_zscore' in self.validation_report:
            outliers = self.validation_report['outliers_zscore']
            all_outlier_indices = set()
            for indices in outliers.values():
                if isinstance(indices, list):
                    all_outlier_indices.update(indices)
            
            df_clean = df_clean.drop(index=list(all_outlier_indices))
            print(f"✓ Removed {len(all_outlier_indices)} outlier rows")
        
        if fill_missing:
            numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if df_clean[col].isna().any():
                    median_val = df_clean[col].median()
                    df_clean[col].fillna(median_val, inplace=True)
            print(f"✓ Filled missing values with median")
        
        return df_clean


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        data_file = sys.argv[1]
        validator = DataValidator(data_file)
        report = validator.run_full_validation()
        validator.save_report('data/quality_reports/validation_report.json')
    else:
        print("Usage: python data_validator.py <path_to_csv>")
