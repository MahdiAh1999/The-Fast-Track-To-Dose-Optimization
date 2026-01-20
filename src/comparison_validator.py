"""
Comparison Validator Module
Compare automated extraction with manual extraction to assess accuracy
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, Tuple
from scipy import stats


class ComparisonValidator:
    """Compare automated vs manual parameter extraction"""
    
    def __init__(self, automated_path: str, manual_path: str):
        """
        Initialize comparison validator
        
        Args:
            automated_path (str): Path to automated extraction CSV
            manual_path (str): Path to manual extraction CSV or Excel
        """
        self.automated_path = automated_path
        self.manual_path = manual_path
        self.df_automated = None
        self.df_manual = None
        self.df_merged = None
        self.comparison_metrics = {}
        
    def load_data(self) -> bool:
        """Load both automated and manual data"""
        try:
            # Load automated extraction
            self.df_automated = pd.read_csv(self.automated_path)
            print(f"✓ Loaded automated data: {len(self.df_automated)} records")
            
            # Load manual extraction (support CSV and Excel)
            if self.manual_path.endswith('.xlsx') or self.manual_path.endswith('.xls'):
                self.df_manual = pd.read_excel(self.manual_path)
            else:
                self.df_manual = pd.read_csv(self.manual_path)
            print(f"✓ Loaded manual data: {len(self.df_manual)} records")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def merge_datasets(self, on_column: str = 'image_file') -> bool:
        """
        Merge automated and manual datasets on common column
        
        Args:
            on_column (str): Column to merge on (usually 'image_file')
            
        Returns:
            bool: Success status
        """
        if self.df_automated is None or self.df_manual is None:
            print("❌ Data not loaded. Call load_data() first.")
            return False
        
        try:
            self.df_merged = pd.merge(
                self.df_automated,
                self.df_manual,
                on=on_column,
                suffixes=('_auto', '_manual'),
                how='inner'
            )
            
            print(f"✓ Merged datasets: {len(self.df_merged)} matching records")
            
            if len(self.df_merged) == 0:
                print("⚠ WARNING: No matching records found!")
                print(f"  Automated files: {list(self.df_automated[on_column].head())}")
                print(f"  Manual files: {list(self.df_manual[on_column].head())}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error merging datasets: {e}")
            return False
    
    def calculate_accuracy_metrics(self, parameters: list = None) -> Dict[str, Dict]:
        """
        Calculate accuracy metrics for each parameter
        
        Args:
            parameters (list): List of parameters to compare
            
        Returns:
            dict: Accuracy metrics for each parameter
        """
        if self.df_merged is None:
            print("❌ No merged data. Call merge_datasets() first.")
            return {}
        
        # Default parameters if not specified
        if parameters is None:
            parameters = [
                'fluoro_time',
                'total_fluoro_kair',
                'dose_entree_peau_max',
                'exposit_ni',
                'total_pds',
                'total_dose',
                'frequence_acquisition'
            ]
        
        metrics = {}
        
        for param in parameters:
            auto_col = f'{param}_auto'
            manual_col = f'{param}_manual'
            
            # Check if columns exist
            if auto_col not in self.df_merged.columns or manual_col not in self.df_merged.columns:
                continue
            
            # Get non-null paired values
            mask = self.df_merged[auto_col].notna() & self.df_merged[manual_col].notna()
            auto_values = self.df_merged.loc[mask, auto_col]
            manual_values = self.df_merged.loc[mask, manual_col]
            
            if len(auto_values) == 0:
                metrics[param] = {'error': 'No valid paired values'}
                continue
            
            # Calculate metrics
            differences = auto_values - manual_values
            abs_differences = np.abs(differences)
            percent_errors = (abs_differences / manual_values.replace(0, np.nan)) * 100
            
            # Agreement metrics
            correlation, p_value = stats.pearsonr(auto_values, manual_values)
            
            # Mean Absolute Percentage Error (MAPE)
            mape = percent_errors.mean()
            
            # Root Mean Square Error (RMSE)
            rmse = np.sqrt(np.mean(differences ** 2))
            
            # Bland-Altman statistics
            mean_diff = differences.mean()
            std_diff = differences.std()
            
            metrics[param] = {
                'n_samples': len(auto_values),
                'mean_absolute_error': abs_differences.mean(),
                'mean_percentage_error': mape,
                'rmse': rmse,
                'correlation': correlation,
                'p_value': p_value,
                'bias': mean_diff,
                'std_diff': std_diff,
                'limits_of_agreement': (mean_diff - 1.96*std_diff, mean_diff + 1.96*std_diff),
                'perfect_match_count': int((differences == 0).sum()),
                'within_5pct_count': int((percent_errors <= 5).sum()),
                'within_10pct_count': int((percent_errors <= 10).sum())
            }
        
        self.comparison_metrics = metrics
        return metrics
    
    def print_comparison_report(self):
        """Print comprehensive comparison report"""
        if not self.comparison_metrics:
            print("❌ No metrics calculated. Call calculate_accuracy_metrics() first.")
            return
        
        print("\n" + "="*80)
        print("AUTOMATED vs MANUAL EXTRACTION COMPARISON REPORT")
        print("="*80)
        
        for param, metrics in self.comparison_metrics.items():
            if 'error' in metrics:
                print(f"\n{param.upper()}: {metrics['error']}")
                continue
            
            print(f"\n{param.upper().replace('_', ' ')}:")
            print(f"  Sample size: {metrics['n_samples']}")
            print(f"  Correlation: {metrics['correlation']:.4f} (p={metrics['p_value']:.4f})")
            print(f"  Mean Absolute Error: {metrics['mean_absolute_error']:.2f}")
            print(f"  MAPE: {metrics['mean_percentage_error']:.2f}%")
            print(f"  RMSE: {metrics['rmse']:.2f}")
            print(f"  Bias: {metrics['bias']:.2f} ± {metrics['std_diff']:.2f}")
            print(f"  Perfect matches: {metrics['perfect_match_count']}/{metrics['n_samples']}")
            print(f"  Within 5% error: {metrics['within_5pct_count']}/{metrics['n_samples']} ({metrics['within_5pct_count']/metrics['n_samples']*100:.1f}%)")
            print(f"  Within 10% error: {metrics['within_10pct_count']}/{metrics['n_samples']} ({metrics['within_10pct_count']/metrics['n_samples']*100:.1f}%)")
        
        print("\n" + "="*80 + "\n")
    
    def create_bland_altman_plot(self, parameter: str, output_path: str = None):
        """
        Create Bland-Altman plot for a parameter
        
        Args:
            parameter (str): Parameter name
            output_path (str): Path to save plot
        """
        if self.df_merged is None:
            print("❌ No merged data available.")
            return
        
        auto_col = f'{parameter}_auto'
        manual_col = f'{parameter}_manual'
        
        if auto_col not in self.df_merged.columns or manual_col not in self.df_merged.columns:
            print(f"❌ Parameter '{parameter}' not found in merged data.")
            return
        
        # Get paired values
        mask = self.df_merged[auto_col].notna() & self.df_merged[manual_col].notna()
        auto_values = self.df_merged.loc[mask, auto_col]
        manual_values = self.df_merged.loc[mask, manual_col]
        
        # Calculate Bland-Altman statistics
        mean_values = (auto_values + manual_values) / 2
        differences = auto_values - manual_values
        mean_diff = differences.mean()
        std_diff = differences.std()
        
        # Create plot
        plt.figure(figsize=(10, 6))
        plt.scatter(mean_values, differences, alpha=0.6)
        plt.axhline(mean_diff, color='red', linestyle='--', label=f'Mean difference: {mean_diff:.2f}')
        plt.axhline(mean_diff + 1.96*std_diff, color='gray', linestyle='--', label=f'±1.96 SD: {mean_diff + 1.96*std_diff:.2f}')
        plt.axhline(mean_diff - 1.96*std_diff, color='gray', linestyle='--', label=f'±1.96 SD: {mean_diff - 1.96*std_diff:.2f}')
        plt.axhline(0, color='black', linestyle='-', alpha=0.3)
        
        plt.xlabel('Mean of Automated and Manual', fontsize=12)
        plt.ylabel('Difference (Automated - Manual)', fontsize=12)
        plt.title(f'Bland-Altman Plot: {parameter.replace("_", " ").title()}', fontsize=14, fontweight='bold')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved to: {output_path}")
        
        plt.show()
    
    def create_correlation_plots(self, output_folder: str = None):
        """
        Create correlation scatter plots for all parameters
        
        Args:
            output_folder (str): Folder to save plots
        """
        if self.df_merged is None:
            print("❌ No merged data available.")
            return
        
        # Get parameter list
        auto_cols = [col for col in self.df_merged.columns if col.endswith('_auto')]
        parameters = [col.replace('_auto', '') for col in auto_cols]
        
        # Create subplots
        n_params = len(parameters)
        n_cols = 3
        n_rows = (n_params + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
        axes = axes.flatten() if n_params > 1 else [axes]
        
        for idx, param in enumerate(parameters):
            auto_col = f'{param}_auto'
            manual_col = f'{param}_manual'
            
            if auto_col not in self.df_merged.columns or manual_col not in self.df_merged.columns:
                continue
            
            ax = axes[idx]
            
            # Get paired values
            mask = self.df_merged[auto_col].notna() & self.df_merged[manual_col].notna()
            auto_values = self.df_merged.loc[mask, auto_col]
            manual_values = self.df_merged.loc[mask, manual_col]
            
            # Scatter plot
            ax.scatter(manual_values, auto_values, alpha=0.6)
            
            # Perfect agreement line
            min_val = min(manual_values.min(), auto_values.min())
            max_val = max(manual_values.max(), auto_values.max())
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', label='Perfect agreement')
            
            # Calculate correlation
            if len(auto_values) > 1:
                corr, _ = stats.pearsonr(auto_values, manual_values)
                ax.text(0.05, 0.95, f'r = {corr:.3f}', transform=ax.transAxes, 
                       verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel('Manual Extraction', fontsize=10)
            ax.set_ylabel('Automated Extraction', fontsize=10)
            ax.set_title(param.replace('_', ' ').title(), fontsize=11, fontweight='bold')
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
        
        # Hide empty subplots
        for idx in range(n_params, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        
        if output_folder:
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            plt.savefig(f"{output_folder}/correlation_plots.png", dpi=300, bbox_inches='tight')
            print(f"✓ Correlation plots saved to: {output_folder}/correlation_plots.png")
        
        plt.show()
    
    def save_comparison_report(self, output_path: str):
        """Save comparison metrics to CSV"""
        if not self.comparison_metrics:
            print("❌ No metrics to save. Call calculate_accuracy_metrics() first.")
            return False
        
        try:
            # Convert metrics dict to DataFrame
            rows = []
            for param, metrics in self.comparison_metrics.items():
                if 'error' in metrics:
                    continue
                row = {'parameter': param}
                row.update(metrics)
                # Flatten limits_of_agreement tuple
                if 'limits_of_agreement' in metrics:
                    row['loa_lower'] = metrics['limits_of_agreement'][0]
                    row['loa_upper'] = metrics['limits_of_agreement'][1]
                    del row['limits_of_agreement']
                rows.append(row)
            
            df_metrics = pd.DataFrame(rows)
            df_metrics.to_csv(output_path, index=False)
            print(f"✓ Comparison report saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving report: {e}")
            return False


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 2:
        auto_file = sys.argv[1]
        manual_file = sys.argv[2]
        
        validator = ComparisonValidator(auto_file, manual_file)
        
        if validator.load_data():
            if validator.merge_datasets():
                metrics = validator.calculate_accuracy_metrics()
                validator.print_comparison_report()
                validator.create_correlation_plots('results/visualizations/')
                validator.save_comparison_report('results/comparison_metrics.csv')
    else:
        print("Usage: python comparison_validator.py <automated_csv> <manual_csv_or_xlsx>")
