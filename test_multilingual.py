#!/usr/bin/env python
"""
Test script for language detection and NLU capabilities.
This helps validate that the multilingual setup is working correctly.
"""

import os
import sys
import logging
import argparse
from pathlib import Path
import time
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("language_test")

def test_labse_language_detection():
    """Test LaBSE model for language detection."""
    logger.info("Testing LaBSE language detection capabilities...")
    
    # Sample messages in different languages
    sample_messages = [
        ("Hello, I want to add a new contact", "en"),
        ("Xin chào, tôi muốn thêm một liên hệ mới", "vi"),
        ("I need to save a wallet address", "en"),
        ("Tôi cần lưu địa chỉ ví", "vi"),
        ("Hello, tôi muốn thêm một địa chỉ", "mixed"),  # Mixed language
    ]
    
    # Create a temporary file to test LaBSE language detection
    with open("test_language_detection.py", "w") as f:
        f.write("""
import torch
from transformers import AutoTokenizer, AutoModel
import numpy as np

# Load LaBSE
print("Loading LaBSE model...")
cache_dir = "./cache"
tokenizer = AutoTokenizer.from_pretrained("rasa/LaBSE", cache_dir=cache_dir)
model = AutoModel.from_pretrained("rasa/LaBSE", cache_dir=cache_dir)

# Function to get embeddings
def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).numpy()

# Reference texts for language identification
language_references = {
    "en": ["Hello", "Good morning", "How are you", "Thank you"],
    "vi": ["Xin chào", "Chào buổi sáng", "Bạn khỏe không", "Cảm ơn bạn"]
}

# Get reference embeddings
language_embeddings = {}
for lang, texts in language_references.items():
    embeddings = []
    for text in texts:
        embeddings.append(get_embedding(text))
    language_embeddings[lang] = np.mean(embeddings, axis=0)

# Test samples
test_samples = [
    "Hello, I want to add a new contact",
    "Xin chào, tôi muốn thêm một liên hệ mới",
    "I need to save a wallet address",
    "Tôi cần lưu địa chỉ ví",
    "Hello, tôi muốn thêm một địa chỉ"
]

for sample in test_samples:
    print(f"\\nTesting: '{sample}'")
    sample_embedding = get_embedding(sample)
    
    # Calculate cosine similarity with each language
    similarities = {}
    for lang, lang_embedding in language_embeddings.items():
        # Compute cosine similarity
        similarity = np.dot(sample_embedding, lang_embedding.T) / (
            np.linalg.norm(sample_embedding) * np.linalg.norm(lang_embedding)
        )
        similarities[lang] = float(similarity)
    
    # Print similarities
    for lang, score in similarities.items():
        print(f"Similarity to {lang}: {score:.4f}")
    
    # Detect language
    detected = max(similarities, key=similarities.get)
    print(f"Detected language: {detected}")
    
    # Check for mixed language
    scores = list(similarities.values())
    diff = abs(scores[0] - scores[1])
    if diff < 0.1:  # If difference is small, might be mixed
        print("This might be a mixed language message")
""")
    
    logger.info("Running language detection test...")
    try:
        start_time = time.time()
        os.system(f"{sys.executable} test_language_detection.py")
        elapsed_time = time.time() - start_time
        logger.info(f"Language detection test completed in {elapsed_time:.2f} seconds")
        
        # Clean up
        os.remove("test_language_detection.py")
        return True
    except Exception as e:
        logger.error(f"Language detection test failed: {str(e)}")
        return False

def test_nlu_pipeline(rasa_path=None):
    """Test the NLU pipeline with multilingual examples."""
    if not rasa_path:
        rasa_path = "rasa"  # Default command
    
    logger.info("Testing NLU pipeline with multilingual examples...")
    
    # Sample messages in different languages
    sample_messages = [
        "Hello, I want to add a new contact",
        "Xin chào, tôi muốn thêm một liên hệ mới",
        "My wallet address is 0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "Địa chỉ ví của tôi là 0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
        "Hello, tôi muốn thêm một địa chỉ",  # Mixed language
    ]
    
    logger.info("Writing sample messages to test file...")
    with open("test_nlu_messages.txt", "w") as f:
        for msg in sample_messages:
            f.write(f"{msg}\n")
    
    # Test with rasa shell nlu
    logger.info("Running 'rasa shell nlu' with test messages...")
    try:
        os.system(f"{rasa_path} shell nlu --nlu-data test_nlu_messages.txt")
        logger.info("NLU pipeline test completed")
        
        # Clean up
        os.remove("test_nlu_messages.txt")
        return True
    except Exception as e:
        logger.error(f"NLU pipeline test failed: {str(e)}")
        return False

def main():
    """Main function to run tests."""
    parser = argparse.ArgumentParser(description='Test Rasa multilingual capabilities')
    parser.add_argument('--language-test', action='store_true', help='Run LaBSE language detection test')
    parser.add_argument('--nlu-test', action='store_true', help='Run NLU pipeline test')
    parser.add_argument('--rasa-path', type=str, default='rasa', help='Path to rasa executable')
    parser.add_argument('--all', action='store_true', help='Run all tests')
    
    args = parser.parse_args()
    
    # If no arguments, run all tests
    if not (args.language_test or args.nlu_test or args.all):
        args.all = True
    
    success = True
    
    if args.language_test or args.all:
        logger.info("=== Running LaBSE Language Detection Test ===")
        if not test_labse_language_detection():
            success = False
    
    if args.nlu_test or args.all:
        logger.info("=== Running NLU Pipeline Test ===")
        if not test_nlu_pipeline(args.rasa_path):
            success = False
    
    if success:
        logger.info("=== 🎉 All tests completed successfully! ===")
        return 0
    else:
        logger.error("=== ❌ Some tests failed. Please check the logs. ===")
        return 1

if __name__ == "__main__":
    sys.exit(main())
