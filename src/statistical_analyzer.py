"""
Statistical Analyzer Module
Calculate DRLs (3rd quartile) from extracted parameters
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


class StatisticalAnalyzer: 
    """Analyze dosimetric parameters and calculate DRLs"""
    
    def __init__(self, data_path):
        """
        Initialize the analyzer
        
        Args:
            data_path (str): Path to CSV file with extracted parameters
        """
        self.data_path = data_path
        self.df = None
        self.drls = None
        
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
        
        # Create DataFrame with DRLs
        drl_df = pd.DataFrame({
            'Parameter': self.drls.index,
            'DRL_Value (75th percentile)': self.drls.values
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