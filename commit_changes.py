#!/usr/bin/env python
"""
Script to commit and push changes to GitHub
Workaround for PowerShell terminal issues
"""

import subprocess
import sys
from pathlib import Path

# Change to project directory
project_dir = Path(__file__).parent
print(f"Working in: {project_dir}")

try:
    # Stage all changes
    print("\n1. Staging all changes...")
    result = subprocess.run(
        ["git", "add", "."],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error staging files: {result.stderr}")
        sys.exit(1)
    print("✓ Files staged successfully")
    
    # Check status
    print("\n2. Checking git status...")
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    
    # Commit with message
    print("\n3. Committing changes...")
    commit_message = """Add comprehensive error handling and complete notebook documentation

- Enhanced parameter_extractor.py with try-except blocks and empty text detection
- Enhanced image_processor.py with file validation and preprocessing error handling
- Created detailed notebooks/README.md with complete workflows for all 3 notebooks
- Notebooks now include full implementation with quality assessment, extraction, and validation"""
    
    result = subprocess.run(
        ["git", "commit", "-m", commit_message],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error committing: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    print("✓ Changes committed successfully")
    
    # Push to GitHub
    print("\n4. Pushing to GitHub...")
    result = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=project_dir,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Error pushing: {result.stderr}")
        sys.exit(1)
    print(result.stdout)
    print("✓ Changes pushed to GitHub successfully")
    
    print("\n✅ All changes committed and pushed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
