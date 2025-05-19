#!/usr/bin/env python
"""
Test the Vietnamese tokenizer integration with Rasa.
"""

import logging
import sys
from rasa.core.utils import set_log_level
from rasa.shared.nlu.training_data.message import Message
from components.multilingual import UnderthesaTokenizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Test the Vietnamese tokenizer."""
    set_log_level(logging.INFO)
    
    # Test sentences
    test_samples = [
        {
            "text": "Xin chào, tôi muốn thêm một liên hệ mới",
            "language": "vi",
            "label": "Vietnamese"
        },
        {
            "text": "Hello, I want to add a new contact",
            "language": "en",
            "label": "English"
        },
        {
            "text": "Tôi cần lưu địa chỉ ví Bitcoin của John",
            "language": "vi",
            "label": "Vietnamese with named entity"
        },
        {
            "text": "Hello, tôi muốn thêm một địa chỉ",
            "language": "vi",  # Mark as Vietnamese for tokenization
            "label": "Mixed language"
        }
    ]
    
    # Initialize tokenizer
    tokenizer = UnderthesaTokenizer({
        "intent_tokenization_flag": True,
        "intent_split_symbol": "_"
    })
    
    # Test each sample
    for sample in test_samples:
        text = sample["text"]
        language = sample.get("language", "")
        label = sample["label"]
        
        logger.info(f"\nTesting {label}: '{text}'")
        
        # Create a Message object
        message = Message({"text": text})
        if language:
            # Set language in the message metadata
            message.set("language", language)
        
        # Tokenize
        tokens = tokenizer.tokenize(message, "text")
        
        # Print results
        logger.info(f"Language: {language}")
        logger.info(f"Tokens: {[t.text for t in tokens]}")
    
    logger.info("\nTest completed successfully. If you see Vietnamese tokens properly segmented, the tokenizer is working.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
