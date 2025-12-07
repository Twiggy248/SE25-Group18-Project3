import pytest, os, sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set TESTING environment variable for the entire test session
os.environ["TESTING"] = "true"

# Mock the model and tokenizer loading before any tests import main.py
@pytest.fixture(scope="session", autouse=True)
def mock_model_loading():
    """Mock heavy model loading for tests"""
    # Only mock what's actually imported when TESTING=true
    # Since we have conditional imports, we don't need to patch transformers imports
    
    yield {
        'testing_mode': True
    }