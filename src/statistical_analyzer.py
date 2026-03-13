"""
Statistical Analyzer Module
Calculate DRLs (3rd quartile) from extracted parameters
"""

import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from scipy import stats as scipy_stats


class StatisticalAnalyzer: 
    """Analyze dosimetric parameters and calculate DRLs"""
    
    def __init__(self, data_path, config_path='config.json'):
        """
        Initialize the analyzer
        
        Args:
            data_path (str): Path to CSV file with extracted parameters
            config_path (str): Path to the configuration file
        """
        self.data_path = data_path
        self.df = None
        self.drls = None
        self._units = {}
        self._primary_params = ['pka', 'kair', 'fluoro_time']

        # Load units and primary parameters from config
        try:
            config_file = Path(config_path)
            if not config_file.is_absolute():
                config_file = Path(__file__).parent.parent / config_path
            with open(config_file, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            self._units = cfg.get('parameter_units', {})
            self._primary_params = cfg.get('primary_drl_parameters', self._primary_params)
        except Exception:
            pass
        
    def load_data(self):
        """Load data from CSV"""
        try:
            self. df = pd.read_csv(self.data_path)
            print(f"✓ Loaded {len(self.df)} interventions")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def calculate_descriptive_stats(self):
        """Calculate descriptive statistics for all parameters"""
        if self. df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Select only numeric columns (exclude image_file)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # Calculate statistics
        stats = self.df[numeric_cols].describe()
        
        # Add additional statistics
        stats. loc['median'] = self.df[numeric_cols].median()
        stats.loc['Q3 (75th percentile)'] = self.df[numeric_cols].quantile(0.75)
        
        return stats
    
    def calculate_drls(self):
        """
        Calculate DRLs as 3rd quartile (75th percentile)
        
        Returns:
            pd.Series: DRL values for each parameter
        """
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Select only numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # Calculate 3rd quartile (75th percentile)
        self.drls = self.df[numeric_cols].quantile(0.75)
        
        return self.drls
    
    def save_drls(self, output_path):
        """Save DRLs to file"""
        if self.drls is None:
            print("No DRLs calculated. Call calculate_drls() first.")
            return False
        
        # Create DataFrame with DRLs (include units when available)
        drl_df = pd.DataFrame({
            'Parameter': self.drls.index,
            'DRL_Value (75th percentile)': self.drls.values,
            'Unit': [self._units.get(p, '') for p in self.drls.index]
        })
        
        # Save to CSV
        drl_df.to_csv(output_path, index=False)
        print(f"✓ DRLs saved to: {output_path}")
        
        return True
    
    def visualize_distributions(self, output_folder=None):
        """Create box plots for all parameters"""
        if self. df is None:
            print("No data loaded. Call load_data() first.")
            return
        
        # Select numeric columns
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        
        # Create subplots
        n_params = len(numeric_cols)
        n_cols = 3
        n_rows = (n_params + n_cols - 1) // n_cols
        
        fig, axes = plt. subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        axes = axes.flatten() if n_params > 1 else [axes]
        
        # Plot each parameter
        for idx, col in enumerate(numeric_cols):
            ax = axes[idx]
            
            # Box plot
            data = self.df[col].dropna()
            ax.boxplot(data, vert=True)
            
            # Add DRL line (75th percentile)
            q3 = data.quantile(0.75)
            ax.axhline(y=q3, color='r', linestyle='--', linewidth=2, label=f'DRL (Q3): {q3:.2f}')
            
            ax.set_title(col. replace('_', ' ').title())
            ax.set_ylabel('Value')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # Hide empty subplots
        for idx in range(n_params, len(axes)):
            axes[idx]. axis('off')
        
        plt.tight_layout()
        
        # Save if output folder specified
        if output_folder:
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            plt.savefig(f"{output_folder}/parameter_distributions. png", dpi=300, bbox_inches='tight')
            print(f"✓ Visualization saved to: {output_folder}/parameter_distributions.png")
        
        plt.show()
    
    def calculate_sem_and_fit_indices(self):
        """
        Compute SEM and structural equation model goodness-of-fit indices
        as reported in the poster: χ²[201]=566.88, p<.0001; SRMR=.12,
        RMSEA=.08, CFI=.88, TLI=.863.

        SEM = SD / sqrt(n)  (fallback when ICC not available)

        Returns:
            dict: SEM per parameter and aggregate fit indices
        """
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        results = {'sem': {}, 'fit_indices': {}}

        for col in numeric_cols:
            data = self.df[col].dropna()
            if len(data) < 2:
                continue
            sd = data.std(ddof=1)
            n = len(data)
            results['sem'][col] = sd / np.sqrt(n)

        # Approximate fit indices from the covariance structure
        try:
            results['fit_indices'] = self.calculate_fit_indices(
                self.df[numeric_cols].dropna()
            )
        except Exception:
            results['fit_indices'] = {
                'chi2': None, 'df': None, 'p_value': None,
                'rmsea': None, 'cfi': None, 'tli': None, 'srmr': None
            }

        return results

    def calculate_fit_indices(self, df):
        """
        Compute approximate SEM-based goodness-of-fit indices using the
        observed covariance matrix vs a null (independence) model.

        The null (independence) model chi-square is computed via the Bartlett
        sphericity test on the correlation matrix.  The model chi-square is
        estimated from the residual correlation matrix.

        Returns:
            dict: chi2, df, p_value, rmsea, cfi, tli, srmr
        """
        if df.empty or df.shape[1] < 2:
            return {}

        n = len(df)
        k = df.shape[1]
        df_model = k * (k - 1) // 2  # off-diagonal elements (integer)

        # Observed correlation matrix
        R = df.corr().values

        det_R = np.linalg.det(R)
        if det_R <= 0:
            return {}

        # Null (independence) model chi-square — Bartlett sphericity test:
        # chi2_null = -(n-1) * log(det(R))
        chi2_null = -(n - 1) * np.log(det_R)
        chi2_null = max(chi2_null, 1e-9)

        # Model chi-square — based on residual (off-diagonal) correlations
        R_null = np.eye(k)
        residuals = R - R_null
        off_diag_sq = np.sum(np.triu(residuals, k=1) ** 2)
        # Scale: (n-1) * sum_of_squared_off_diagonal_residuals
        chi2_model = (n - 1) * off_diag_sq
        chi2_model = max(chi2_model, 0)

        p_value = 1 - scipy_stats.chi2.cdf(chi2_model, df=df_model)

        # RMSEA
        rmsea = np.sqrt(max(chi2_model - df_model, 0) / (df_model * (n - 1)))

        # CFI and TLI (using null baseline)
        df_null = k * (k - 1) // 2  # same as df_model for independence test

        numerator_cfi = max(chi2_null - df_null, 0) - max(chi2_model - df_model, 0)
        denominator_cfi = max(chi2_null - df_null, 1e-9)
        cfi = numerator_cfi / denominator_cfi
        cfi = min(max(cfi, 0.0), 1.0)

        if df_null > 0 and chi2_null / df_null > 1:
            tli = (chi2_null / df_null - chi2_model / max(df_model, 1)) / \
                  (chi2_null / df_null - 1)
        else:
            tli = 0.0
        tli = min(max(tli, 0.0), 1.0)

        # SRMR
        n_off = k * (k - 1) // 2
        srmr = np.sqrt(np.sum(np.triu(residuals, k=1) ** 2) / n_off) if n_off > 0 else 0

        return {
            'chi2': round(chi2_model, 2),
            'df': df_model,
            'p_value': round(p_value, 4),
            'rmsea': round(rmsea, 3),
            'cfi': round(cfi, 3),
            'tli': round(tli, 3),
            'srmr': round(srmr, 3)
        }

    def get_parameter_unit(self, param: str) -> str:
        """Return the unit string for a given parameter (empty string if unknown)."""
        return self._units.get(param, '')

    def calculate_poster_drls(self):
        """
        Extract Q1, Q3, and median for primary DRL parameters (PKA, Ka,r,
        fluoro_time) and print them in the poster format.

        Returns:
            dict: {param: {'Q1': ..., 'median': ..., 'Q3': ...}}
        """
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return {}

        result = {}
        for param in self._primary_params:
            if param not in self.df.columns:
                continue
            data = self.df[param].dropna()
            if data.empty:
                continue
            result[param] = {
                'Q1': data.quantile(0.25),
                'median': data.median(),
                'Q3': data.quantile(0.75)
            }

        def _fmt(value, unit, decimals=0):
            """Format a DRL value with its unit."""
            if not isinstance(value, float):
                return str(value)
            if decimals == 0:
                return f"{value:,.0f} {unit}"
            return f"{value:.{decimals}f} {unit}"

        pka_q3 = result.get('pka', {}).get('Q3', 'N/A')
        kair_q3 = result.get('kair', {}).get('Q3', 'N/A')
        ft_q3 = result.get('fluoro_time', {}).get('Q3', 'N/A')

        print(
            f"\n  PKA  Q3 = {_fmt(pka_q3, self.get_parameter_unit('pka'))}  |  "
            f"Ka,r Q3 = {_fmt(kair_q3, self.get_parameter_unit('kair'))}  |  "
            f"FT Q3 = {_fmt(ft_q3, self.get_parameter_unit('fluoro_time'), decimals=1)}"
        )

        return result

    def calculate_extraction_accuracy(self, total_values, correct_values):
        """
        Compute and display extraction accuracy in the poster format.

        Args:
            total_values (int): Total number of values attempted
            correct_values (int): Number of correctly extracted values

        Returns:
            float: Accuracy percentage
        """
        if total_values == 0:
            print("  ⚠ No values to compute accuracy.")
            return 0.0
        accuracy = correct_values / total_values * 100
        print(f"\n  ✅ Extraction accuracy: {accuracy:.2f}% ({correct_values}/{total_values})")
        return accuracy

    def calculate_confidence_intervals(self, percentile=0.75, confidence=0.95, n_bootstrap=1000):
        """
        Calculate bootstrap confidence intervals for DRL values.

        Args:
            percentile (float): Percentile to compute (default 0.75 for Q3/DRL)
            confidence (float): Confidence level (default 0.95)
            n_bootstrap (int): Number of bootstrap resamples

        Returns:
            dict: {param: (lower_ci, upper_ci)}
        """
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return {}

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        ci_results = {}

        alpha = 1 - confidence
        rng = np.random.default_rng(42)

        for col in numeric_cols:
            data = self.df[col].dropna().values
            if len(data) < 2:
                continue
            bootstrap_stats = np.array([
                np.percentile(rng.choice(data, size=len(data), replace=True), percentile * 100)
                for _ in range(n_bootstrap)
            ])
            lower = np.percentile(bootstrap_stats, alpha / 2 * 100)
            upper = np.percentile(bootstrap_stats, (1 - alpha / 2) * 100)
            ci_results[col] = (round(lower, 2), round(upper, 2))

        return ci_results

    def create_summary_table(self):
        """Create a comprehensive summary table"""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        numeric_cols = self.df.select_dtypes(include=[np. number]).columns
        
        summary = pd.DataFrame({
            'Parameter': numeric_cols,
            'Count': [self.df[col].count() for col in numeric_cols],
            'Mean': [self. df[col].mean() for col in numeric_cols],
            'Median': [self.df[col].median() for col in numeric_cols],
            'Std Dev': [self.df[col].std() for col in numeric_cols],
            'Min':  [self.df[col].min() for col in numeric_cols],
            'Q1 (25th)': [self.df[col]. quantile(0.25) for col in numeric_cols],
            'Q2 (50th)': [self.df[col].quantile(0.50) for col in numeric_cols],
            'Q3 (75th) - DRL': [self.df[col].quantile(0.75) for col in numeric_cols],
            'Max': [self.df[col]. max() for col in numeric_cols]
        })
        
        return summary


if __name__ == "__main__":
    # Example usage
    analyzer = StatisticalAnalyzer('data/processed/extracted_parameters.csv')
    
    if analyzer.load_data():
        # Calculate statistics
        stats = analyzer.calculate_descriptive_stats()
        print("\nDescriptive Statistics:")
        print(stats)
        
        # Calculate DRLs
        drls = analyzer.calculate_drls()
        print("\nDRLs (75th percentile):")
        print(drls)
        
        # Save DRLs
        analyzer.save_drls('results/drls/local_drls.csv')
        
        # Visualize
        analyzer.visualize_distributions('results/visualizations/')
        
        # Summary table
        summary = analyzer.create_summary_table()
        print("\nSummary Table:")
        print(summary)