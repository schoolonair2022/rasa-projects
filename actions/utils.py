"""Utility functions for Rasa actions"""

import logging
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Singleton pattern for model loading
class CryptoBERTManager:
    _instance = None
    model = None
    tokenizer = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CryptoBERTManager, cls).__new__(cls)
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load CryptoBERT model and tokenizer"""
        try:
            logger.info("Loading CryptoBERT model...")
            MODEL_NAME = "ElKulako/cryptobert"
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            logger.info("CryptoBERT model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CryptoBERT model: {str(e)}")
            self.tokenizer = None
            self.model = None
    
    def classify_text(self, text, threshold=0.7):
        """Classify text using CryptoBERT"""
        if self.tokenizer is None or self.model is None:
            logger.warning("CryptoBERT model not available")
            return None
        
        try:
            # Prepare the input text
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            # Get model prediction
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get the highest probability class
            score = predictions[0].max().item()
            predicted_class = predictions[0].argmax().item()
            
            logger.info(f"CryptoBERT classification - Class: {predicted_class}, Score: {score}")
            
            # Return boolean based on threshold
            return score > threshold
            
        except Exception as e:
            logger.error(f"Error classifying with CryptoBERT: {str(e)}")
            return None

# Wallet address validation utilities
def is_valid_ethereum_address(address):
    """Validate Ethereum address format"""
    import re
    # Ethereum addresses are 42 characters, starting with 0x followed by 40 hex chars
    eth_pattern = r'^0x[a-fA-F0-9]{40}$'
    return bool(re.match(eth_pattern, address))

def is_valid_bitcoin_address(address):
    """Validate Bitcoin address format"""
    import re
    # Simple pattern for Bitcoin addresses (P2PKH, P2SH, and Bech32)
    btc_pattern = r'^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$'
    return bool(re.match(btc_pattern, address))

def validate_crypto_address(address):
    """Comprehensive validation for crypto addresses"""
    # First try regex patterns
    if is_valid_ethereum_address(address):
        logger.info(f"Address {address} validated by ETH regex pattern")
        return True, "ETH"
    elif is_valid_bitcoin_address(address):
        logger.info(f"Address {address} validated by BTC regex pattern")
        return True, "BTC"
    else:
        logger.info(f"Address {address} failed regex validation, trying CryptoBERT...")
        # Fall back to CryptoBERT for more complex cases
        try:
            bert_manager = CryptoBERTManager()
            is_valid = bert_manager.classify_text(address)
            logger.info(f"CryptoBERT classification result for {address}: {is_valid}")
            if is_valid:
                return True, "CRYPTO"  # Generic crypto type
            return False, None
        except Exception as e:
            logger.error(f"Error in CryptoBERT validation: {str(e)}")
            return False, None
