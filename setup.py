#!/usr/bin/env python
"""
Setup script for Rasa project with LaBSE support.
This script verifies the environment, downloads the LaBSE model,
and tests the tokenizers.
"""

import os
import sys
import subprocess
import tempfile
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup")

def check_python_version():
    """Check if Python version is compatible."""
    logger.info("Checking Python version...")
    python_version = sys.version_info
    if python_version.major == 3 and 8 <= python_version.minor <= 10:
        logger.info(f"✅ Python version is compatible: {python_version.major}.{python_version.minor}.{python_version.micro}")
        return True
    else:
        logger.error(f"❌ Python version {python_version.major}.{python_version.minor}.{python_version.micro} is not compatible. Please use Python 3.8-3.10.")
        return False

def check_dependencies():
    """Check if all required dependencies are installed."""
    logger.info("Checking dependencies...")
    
    # List of required packages
    requirements_file = Path("requirements.txt")
    if not requirements_file.exists():
        logger.error("❌ requirements.txt not found.")
        return False
        
    with open(requirements_file, "r") as f:
        required_packages = [line.strip().split("==")[0] for line in f if line.strip() and not line.startswith("#")]
    
    # Check each package
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            logger.info(f"✅ Package {package} is installed.")
        except ImportError:
            logger.warning(f"❌ Package {package} is not installed.")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        logger.info("All required packages are installed.")
        return True

def check_labse_model():
    """Check if LaBSE model is available and functioning."""
    logger.info("Checking LaBSE model...")
    
    # Create a temporary file to test LaBSE loading
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as tmp:
        tmp.write("""
import os
from transformers import AutoTokenizer, AutoModel

# Create cache directory
cache_dir = "./cache"
os.makedirs(cache_dir, exist_ok=True)

# Try loading LaBSE
try:
    print("Loading LaBSE tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained("rasa/LaBSE", cache_dir=cache_dir)
    print("Loading LaBSE model...")
    model = AutoModel.from_pretrained("rasa/LaBSE", cache_dir=cache_dir)
    print("Successfully loaded LaBSE model!")
    
    # Test with a sample sentence
    print("Testing embedding generation...")
    inputs = tokenizer("Hello, world!", return_tensors="pt")
    outputs = model(**inputs)
    embedding = outputs.last_hidden_state.mean(dim=1)
    print(f"Embedding shape: {embedding.shape}")
    print("LaBSE model is working correctly!")
except Exception as e:
    print(f"Error loading LaBSE model: {str(e)}")
    exit(1)
""")
        tmp.flush()
        
        # Run the test script
        logger.info("Testing LaBSE model loading...")
        start_time = time.time()
        process = subprocess.run([sys.executable, tmp.name], capture_output=True, text=True)
        elapsed_time = time.time() - start_time
        
        if process.returncode == 0:
            logger.info(f"✅ LaBSE model loaded successfully in {elapsed_time:.2f} seconds.")
            logger.info(process.stdout)
            return True
        else:
            logger.error(f"❌ Failed to load LaBSE model.")
            logger.error(process.stderr)
            return False

def check_underthesea():
    """Check if underthesea works properly."""
    logger.info("Checking underthesea for Vietnamese tokenization...")
    
    # Create a temporary file to test underthesea
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as tmp:
        tmp.write("""
try:
    from underthesea import word_tokenize
    
    # Test with Vietnamese text
    text = "Xin chào, tôi muốn thêm một địa chỉ ví vào danh bạ của tôi."
    tokens = word_tokenize(text)
    
    print(f"Original: {text}")
    print(f"Tokenized: {' | '.join(tokens)}")
    print("underthesea is working correctly!")
except Exception as e:
    print(f"Error using underthesea: {str(e)}")
    exit(1)
""")
        tmp.flush()
        
        # Run the test script
        process = subprocess.run([sys.executable, tmp.name], capture_output=True, text=True)
        
        if process.returncode == 0:
            logger.info("✅ underthesea is working properly.")
            logger.info(process.stdout)
            return True
        else:
            logger.error("❌ Failed to use underthesea.")
            logger.error(process.stderr)
            return False

def test_custom_tokenizer():
    """Test that the custom tokenizer works."""
    logger.info("Testing custom tokenizer...")
    
    # Create a temporary file to test custom tokenizer
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".py") as tmp:
        tmp.write("""
import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

try:
    from custom.tokenizers import UnderthesaTokenizer
    
    # Create a mock message
    class MockMessage:
        def __init__(self, text):
            self.text = text
            
        def get(self, attr):
            if attr == "text":
                return self.text
            return None
    
    # Create tokenizer
    tokenizer = UnderthesaTokenizer({})
    
    # Test with Vietnamese text
    vi_text = "Xin chào, tôi muốn thêm một địa chỉ ví vào danh bạ của tôi."
    vi_message = MockMessage(vi_text)
    
    # Tokenize
    tokens = tokenizer.tokenize(vi_message, "text")
    
    print(f"Original: {vi_text}")
    print(f"Tokens: {[t.text for t in tokens]}")
    print("Custom tokenizer is working correctly!")
except Exception as e:
    print(f"Error testing custom tokenizer: {str(e)}")
    exit(1)
""")
        tmp.flush()
        
        # Run the test script
        process = subprocess.run([sys.executable, tmp.name], capture_output=True, text=True)
        
        if process.returncode == 0:
            logger.info("✅ Custom tokenizer is working properly.")
            logger.info(process.stdout)
            return True
        else:
            logger.error("❌ Failed to test custom tokenizer.")
            logger.error(process.stderr)
            return False

def check_hardware():
    """Check if hardware meets requirements."""
    logger.info("Checking hardware requirements...")
    
    # Check available memory
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_count = psutil.cpu_count(logical=False)
        
        logger.info(f"Available memory: {memory_gb:.2f} GB")
        logger.info(f"CPU cores: {cpu_count}")
        
        if memory_gb >= 20 and cpu_count >= 4:
            logger.info("✅ Hardware meets requirements.")
            return True
        else:
            warnings = []
            if memory_gb < 20:
                warnings.append(f"Low memory ({memory_gb:.2f} GB < 20 GB recommended)")
            if cpu_count < 4:
                warnings.append(f"Low CPU cores ({cpu_count} < 4 recommended)")
                
            logger.warning(f"⚠️ Hardware limitations detected: {', '.join(warnings)}")
            
            # Provide optimization suggestions
            logger.info("Optimization suggestions:")
            if memory_gb < 20:
                logger.info("- Reduce batch_size in config.yml to 8 or 4")
                logger.info("- Set 'cache_dir' to an SSD location")
                logger.info("- Consider using smaller training datasets")
            
            return True  # Return True but with warnings
    except ImportError:
        logger.warning("⚠️ Cannot check hardware requirements (psutil not installed).")
        return True

def setup_environment():
    """Setup the environment by creating necessary directories."""
    logger.info("Setting up environment...")
    
    # Create cache directory
    cache_dir = Path("./cache")
    cache_dir.mkdir(exist_ok=True)
    logger.info(f"✅ Created cache directory at {cache_dir.absolute()}")
    
    # Create models directory if not exists
    models_dir = Path("./models")
    models_dir.mkdir(exist_ok=True)
    logger.info(f"✅ Created models directory at {models_dir.absolute()}")
    
    return True

def main():
    """Main function to run all checks."""
    logger.info("Starting Rasa LaBSE project setup...")
    
    all_checks_passed = True
    
    # Run checks
    if not check_python_version():
        all_checks_passed = False
    
    if not check_dependencies():
        logger.error("Missing dependencies. Please install them with:")
        logger.error("pip install -r requirements.txt")
        all_checks_passed = False
    
    if not setup_environment():
        all_checks_passed = False
    
    if not check_hardware():
        # This doesn't fail, just provides warnings
        pass
    
    if all_checks_passed:
        # Only run these checks if basic dependencies are installed
        if not check_labse_model():
            all_checks_passed = False
        
        if not check_underthesea():
            all_checks_passed = False
            
        if not test_custom_tokenizer():
            all_checks_passed = False
    
    # Final status
    if all_checks_passed:
        logger.info("=== 🎉 All checks passed! You're ready to train your Rasa model. ===")
        logger.info("Next steps:")
        logger.info("1. Train your model with: rasa train")
        logger.info("2. Test the model with: rasa shell")
        logger.info("3. Start the action server with: rasa run actions")
        return 0
    else:
        logger.error("=== ❌ Some checks failed. Please fix the issues before proceeding. ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())
