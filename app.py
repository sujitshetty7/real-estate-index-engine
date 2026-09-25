import sys
import os

# Explicitly add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.api.main import app
