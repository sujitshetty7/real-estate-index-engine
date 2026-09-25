import sys
import os

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, root_dir)

try:
    from src.api.main import app
except ModuleNotFoundError:
    try:
        from api.main import app
    except ModuleNotFoundError:
        print("DEBUG: Root directory files:", os.listdir(root_dir))
        raise
