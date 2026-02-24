#!/usr/bin/env python
"""
NeuralBeat Test Runner
======================

Runs all unit tests for the NeuralBeat project.

Usage:
    python run_tests.py
    python run_tests.py -v    # Verbose output
"""

import subprocess
import sys
import os

# Ensure we're in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

def main():
    print("=" * 60)
    print("NeuralBeat Test Suite")
    print("=" * 60)
    print()
    
    # Run pytest on tests directory
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests", "-v"],
        cwd=project_root
    )
    
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("All tests passed!")
    else:
        print("Some tests failed.")
    print("=" * 60)
    
    sys.exit(result.returncode)


if __name__ == '__main__':
    main()
