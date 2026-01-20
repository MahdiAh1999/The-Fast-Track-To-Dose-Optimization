"""
Configuration Manager
Load and manage project configuration settings
"""

import json
from pathlib import Path
from typing import Dict, Any


class Config:
    """Manage project configuration from config.json"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration
        
        Args:
            config_path (str): Path to config.json file
        """
        if self._config is None:
            self.config_path = Path(config_path)
            self.load_config()
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            print(f"✓ Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            print(f"⚠ Config file not found: {self.config_path}")
            print("Using default configuration...")
            self._config = self._get_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            print("Using default configuration...")
            self._config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return default configuration if config.json is not available"""
        return {
            "ocr": {
                "default_engine": "tesseract",
                "tesseract_lang": "fra+eng",
                "confidence_threshold": 0.5
            },
            "image_quality": {
                "min_resolution": [800, 600],
                "min_brightness": 50,
                "max_brightness": 200,
                "min_contrast": 30,
                "min_sharpness": 100
            },
            "statistics": {
                "drl_percentile": 0.75
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key (str): Configuration key (use dot notation for nested keys, e.g., 'ocr.default_engine')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_ocr_config(self) -> Dict[str, Any]:
        """Get OCR configuration"""
        return self._config.get('ocr', {})
    
    def get_quality_config(self) -> Dict[str, Any]:
        """Get image quality configuration"""
        return self._config.get('image_quality', {})
    
    def get_preprocessing_config(self) -> Dict[str, Any]:
        """Get preprocessing configuration"""
        return self._config.get('preprocessing', {})
    
    def get_extraction_patterns(self) -> Dict[str, Dict[str, str]]:
        """Get parameter extraction patterns"""
        return self._config.get('extraction_patterns', {})
    
    def get_validation_config(self) -> Dict[str, Any]:
        """Get validation configuration"""
        return self._config.get('validation', {})
    
    def get_statistics_config(self) -> Dict[str, Any]:
        """Get statistics configuration"""
        return self._config.get('statistics', {})
    
    def get_file_paths(self) -> Dict[str, str]:
        """Get configured file paths"""
        return self._config.get('file_paths', {})
    
    def update(self, key: str, value: Any):
        """
        Update configuration value
        
        Args:
            key (str): Configuration key (use dot notation for nested keys)
            value: New value
        """
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def save_config(self, output_path: str = None):
        """
        Save current configuration to file
        
        Args:
            output_path (str): Path to save config (default: original config_path)
        """
        if output_path is None:
            output_path = self.config_path
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2, ensure_ascii=False)
            print(f"✓ Configuration saved to {output_path}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def display(self):
        """Display current configuration"""
        print("\n" + "="*60)
        print("CURRENT CONFIGURATION")
        print("="*60)
        print(json.dumps(self._config, indent=2, ensure_ascii=False))
        print("="*60 + "\n")


# Global config instance
config = Config()


if __name__ == "__main__":
    # Test configuration
    cfg = Config()
    cfg.display()
    
    # Test accessing values
    print("\nTesting configuration access:")
    print(f"OCR Engine: {cfg.get('ocr.default_engine')}")
    print(f"Min Resolution: {cfg.get('image_quality.min_resolution')}")
    print(f"DRL Percentile: {cfg.get('statistics.drl_percentile')}")
    
    # Test getting sections
    print(f"\nOCR Config: {cfg.get_ocr_config()}")
    print(f"Quality Config: {cfg.get_quality_config()}")
