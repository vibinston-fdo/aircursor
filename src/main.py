import sys
import os

# Add the project root to the python path so 'src' imports work
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.app import run_app

if __name__ == "__main__":
    run_app()
