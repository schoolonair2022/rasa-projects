"""Advanced crypto utilities using CryptoBERT"""

import logging
import torch
import re
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModelForQuestionAnswering

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Singleton pattern for model management
class CryptoModelManager:
    _instance = None
    models = {}
    tokenizers = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CryptoModelManager, cls).__new__(cls)
            cls._instance._initialize_models()
        return cls._instance
    
    def _initialize_models(self):
        """Initialize CryptoBERT models for different tasks"""
        try:
            logger.info("Loading CryptoBERT models...")
            
            # Base model for general tasks
            self.models['base'] = AutoModelForSequenceClassification.from_pretrained("ElKulako/cryptobert")
            self.tokenizers['base'] = AutoTokenizer.from_pretrained("ElKulako/cryptobert")
            
            # You can fine-tune and add more specialized models
            # self.models['sentiment'] = ...
            # self.models['qa'] = ...
            
            logger.info("CryptoBERT models loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load CryptoBERT models: {str(e)}")
    
    def get_model(self, task='base'):
        """Get model for a specific task"""
        return self.models.get(task), self.tokenizers.get(task)

# Crypto address validation utilities
from .utils import validate_crypto_address

# New utility functions
def analyze_crypto_sentiment(text):
    """Analyze sentiment in crypto-related text"""
    manager = CryptoModelManager()
    model, tokenizer = manager.get_model('base')
    
    if not model or not tokenizer:
        logger.error("Models not available for sentiment analysis")
        return "neutral", 0.0
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # For demonstration; adapt to your actual labels
        sentiment_map = {0: "negative", 1: "neutral", 2: "positive"}
        sentiment_id = predictions[0].argmax().item()
        confidence = predictions[0].max().item()
        
        return sentiment_map.get(sentiment_id, "neutral"), confidence
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return "neutral", 0.0

def classify_crypto_topic(text):
    """Classify crypto query into topics"""
    manager = CryptoModelManager()
    model, tokenizer = manager.get_model('base')
    
    if not model or not tokenizer:
        logger.error("Models not available for topic classification")
        return "general", 0.0
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # For demonstration; adapt to your actual labels
        topic_map = {
            0: "investment", 
            1: "technical", 
            2: "regulatory", 
            3: "security",
            4: "taxation"
        }
        
        topic_id = predictions[0].argmax().item()
        confidence = predictions[0].max().item()
        
        return topic_map.get(topic_id, "general"), confidence
        
    except Exception as e:
        logger.error(f"Error in topic classification: {str(e)}")
        return "general", 0.0

def detect_crypto_scam(text):
    """Detect potential crypto scams"""
    # First check common scam indicators
    scam_indicators = []
    
    # Common red flags in crypto scams
    red_flags = [
        "guaranteed returns", "100x", "no risk", "limited time", 
        "secret", "exclusive group", "pump and dump", "join now",
        "get rich quick", "double your investment", "insider info"
    ]
    
    for flag in red_flags:
        if flag.lower() in text.lower():
            scam_indicators.append(flag)
    
    # Use CryptoBERT for advanced scam detection
    manager = CryptoModelManager()
    model, tokenizer = manager.get_model('base')
    
    if not model or not tokenizer:
        logger.error("Models not available for scam detection")
        return len(scam_indicators) > 0, 0.5, scam_indicators
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # For demonstration; adapt based on your model
        scam_probability = predictions[0][1].item()  # Assuming binary classification
        is_scam = scam_probability > 0.7 or len(scam_indicators) > 1
        
        return is_scam, scam_probability, scam_indicators
        
    except Exception as e:
        logger.error(f"Error in scam detection: {str(e)}")
        return len(scam_indicators) > 0, 0.5, scam_indicators

def extract_crypto_entities(text):
    """Extract crypto-related entities from text"""
    entities = {
        'tokens': [],
        'blockchains': [],
        'projects': []
    }
    
    # Common tokens to detect
    common_tokens = ["BTC", "ETH", "SOL", "DOT", "ADA", "XRP", "USDT", "USDC"]
    common_blockchains = ["Bitcoin", "Ethereum", "Solana", "Polkadot", "Cardano"]
    
    # Simple pattern matching for demo purposes
    for token in common_tokens:
        if re.search(r'\b' + token + r'\b', text, re.IGNORECASE):
            entities['tokens'].append(token)
    
    for chain in common_blockchains:
        if chain.lower() in text.lower():
            entities['blockchains'].append(chain)
    
    # Use CryptoBERT for more sophisticated entity extraction
    manager = CryptoModelManager()
    model, tokenizer = manager.get_model('base')
    
    if not model or not tokenizer:
        logger.error("Models not available for entity extraction")
        return entities
    
    try:
        # Advanced entity extraction would require fine-tuning
        # This is a placeholder for demonstration
        pass
        
    except Exception as e:
        logger.error(f"Error in entity extraction: {str(e)}")
    
    return entities

def determine_expertise_level(text):
    """Determine user's crypto expertise level from their text"""
    # Simple keyword-based heuristics
    beginner_terms = ["what is", "how to", "explain", "basics", "start", "newbie", "beginner"]
    expert_terms = ["liquidity pool", "yield farming", "impermanent loss", "gas optimization", 
                   "smart contract audit", "rollups", "MEV", "tokenomics"]
    
    # Count occurrences
    beginner_count = sum(1 for term in beginner_terms if term.lower() in text.lower())
    expert_count = sum(1 for term in expert_terms if term.lower() in text.lower())
    
    # Use CryptoBERT for more sophisticated expertise detection
    manager = CryptoModelManager()
    model, tokenizer = manager.get_model('base')
    
    if not model or not tokenizer:
        logger.error("Models not available for expertise level detection")
        # Fall back to simple heuristics
        if expert_count > 0:
            return "expert", 0.7
        elif beginner_count > 0:
            return "beginner", 0.7
        else:
            return "intermediate", 0.5
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # For demonstration; adapt based on your model
        expertise_map = {0: "beginner", 1: "intermediate", 2: "expert"}
        level_id = predictions[0].argmax().item()
        confidence = predictions[0].max().item()
        
        return expertise_map.get(level_id, "intermediate"), confidence
        
    except Exception as e:
        logger.error(f"Error in expertise level detection: {str(e)}")
        # Fall back to simple heuristics
        if expert_count > 0:
            return "expert", 0.7
        elif beginner_count > 0:
            return "beginner", 0.7
        else:
            return "intermediate", 0.5

def detect_critical_news(text):
    """Detect if text contains critical crypto news"""
    # Keywords that might indicate critical news
    regulatory_keywords = ["ban", "regulation", "SEC", "law", "compliance", "illegal"]
    security_keywords = ["hack", "breach", "stolen", "exploit", "vulnerability"]
    market_keywords = ["crash", "plummet", "collapse", "bear market", "selloff"]
    
    # Check for keywords
    has_regulatory = any(word in text.lower() for word in regulatory_keywords)
    has_security = any(word in text.lower() for word in security_keywords)
    has_market = any(word in text.lower() for word in market_keywords)
    
    # Use CryptoBERT for more sophisticated news classification
    manager = CryptoModelManager()
    model, tokenizer = manager.get_model('base')
    
    if not model or not tokenizer:
        logger.error("Models not available for news classification")
        # Fall back to keyword matching
        if has_regulatory:
            return "regulatory", 0.7, True
        elif has_security:
            return "security_breach", 0.8, True
        elif has_market:
            return "market_crash", 0.7, True
        else:
            return "general", 0.5, False
    
    try:
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # For demonstration; adapt based on your model
        news_map = {
            0: "regulatory",
            1: "security_breach",
            2: "market_crash",
            3: "partnership",
            4: "tech_update"
        }
        
        news_id = predictions[0].argmax().item()
        category = news_map.get(news_id, "general")
        urgency = predictions[0].max().item()
        
        # Critical categories with high confidence
        is_critical = category in ["regulatory", "security_breach", "market_crash"] and urgency > 0.7
        
        return category, urgency, is_critical
        
    except Exception as e:
        logger.error(f"Error in news classification: {str(e)}")
        # Fall back to keyword matching
        if has_regulatory:
            return "regulatory", 0.7, True
        elif has_security:
            return "security_breach", 0.8, True
        elif has_market:
            return "market_crash", 0.7, True
        else:
            return "general", 0.5, False
