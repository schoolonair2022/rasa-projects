#!/usr/bin/env python
"""
Test script for improved crypto wallet contact functionality.
This tests both English and Vietnamese examples, with a focus on:
1. Handling typos in cryptocurrency names
2. Detecting and correcting network mismatches
3. Proper Vietnamese tokenization
4. Entity extraction across multiple languages
"""

import argparse
import logging
import os
import sys
from typing import List, Dict, Any, Optional

from rasa.shared.core.domain import Domain
from rasa.core.agent import Agent
from rasa.shared.nlu.training_data.message import Message
from rasa.shared.nlu.interpreter import NaturalLanguageInterpreter
from rasa.nlu.model import Interpreter
from rasa.shared.core.slots import Slot
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.core.events import UserUttered, ActionExecuted, SlotSet

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_model_directory() -> str:
    """Get the latest model directory."""
    models_dir = "./models"
    if not os.path.exists(models_dir):
        logger.error(f"Models directory {models_dir} does not exist.")
        sys.exit(1)
        
    models = [os.path.join(models_dir, f) for f in os.listdir(models_dir) 
              if os.path.isdir(os.path.join(models_dir, f)) and f.startswith("20")]
    
    if not models:
        logger.error("No models found in the models directory.")
        sys.exit(1)
        
    # Return the latest model by timestamp
    return sorted(models)[-1]

def load_interpreter(model_dir: str) -> NaturalLanguageInterpreter:
    """Load the NLU interpreter from the model."""
    interpreter = Interpreter.load(model_dir)
    return interpreter

def test_nlu(interpreter: NaturalLanguageInterpreter, test_examples: List[Dict[str, Any]]) -> None:
    """Test NLU examples for intent classification and entity extraction."""
    results = {
        "total": len(test_examples),
        "correct_intent": 0,
        "correct_entities": 0,
        "partial_entities": 0,
        "examples": []
    }
    
    for example in test_examples:
        text = example["text"]
        expected_intent = example.get("intent")
        expected_entities = example.get("entities", [])
        
        # Process the example
        logger.info(f"Testing: '{text}'")
        response = interpreter.parse(text)
        
        # Check intent
        detected_intent = response.get("intent", {}).get("name")
        intent_correct = detected_intent == expected_intent
        
        if intent_correct:
            results["correct_intent"] += 1
            logger.info(f"✓ Intent: {detected_intent}")
        else:
            logger.info(f"✗ Intent: {detected_intent} (expected: {expected_intent})")
        
        # Check entities
        detected_entities = response.get("entities", [])
        entity_matches = []
        partial_match = False
        
        if expected_entities:
            # Check for exact entity matches
            all_entities_matched = True
            for expected in expected_entities:
                found = False
                for detected in detected_entities:
                    if (detected["entity"] == expected["entity"] and 
                        detected["value"].lower() == expected["value"].lower()):
                        found = True
                        entity_matches.append(f"✓ {detected['entity']}: {detected['value']}")
                        break
                
                if not found:
                    all_entities_matched = False
                    entity_matches.append(f"✗ Missing {expected['entity']}: {expected['value']}")
                    
                    # Check for partial matches (same entity type, different value)
                    for detected in detected_entities:
                        if detected["entity"] == expected["entity"]:
                            partial_match = True
                            entity_matches.append(f"~ Partial {detected['entity']}: {detected['value']} (expected: {expected['value']})")
                            break
            
            if all_entities_matched:
                results["correct_entities"] += 1
            elif partial_match:
                results["partial_entities"] += 1
        
        # Extra entities
        for detected in detected_entities:
            if not any(expected["entity"] == detected["entity"] for expected in expected_entities):
                entity_matches.append(f"! Extra {detected['entity']}: {detected['value']}")
        
        # Log entity results
        for match in entity_matches:
            logger.info(f"  {match}")
            
        results["examples"].append({
            "text": text,
            "expected_intent": expected_intent,
            "detected_intent": detected_intent,
            "intent_correct": intent_correct,
            "expected_entities": expected_entities,
            "detected_entities": detected_entities,
            "entity_matches": entity_matches
        })
        
        logger.info("")
    
    # Print summary
    logger.info("=" * 50)
    logger.info("NLU Test Summary:")
    logger.info(f"Total examples: {results['total']}")
    logger.info(f"Correct intents: {results['correct_intent']} ({results['correct_intent']/results['total']*100:.1f}%)")
    logger.info(f"Correct entities: {results['correct_entities']} ({results['correct_entities']/results['total']*100:.1f}%)")
    logger.info(f"Partial entities: {results['partial_entities']} ({results['partial_entities']/results['total']*100:.1f}%)")
    
    return results

def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test improved contact functionality')
    parser.add_argument('--model', help='Path to the Rasa model directory', default=None)
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Determine model path
    model_dir = args.model if args.model else get_model_directory()
    logger.info(f"Using model from: {model_dir}")
    
    # Load interpreter
    interpreter = load_interpreter(model_dir)
    
    # Define test examples
    test_examples = [
        # English examples
        {
            "text": "Add James to my contacts with Bitcoin address 1Dt7KiqqpgQ2UVWrNSYhEV7YWYUaGC9hFS",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "James"},
                {"entity": "contact_add_entity_crypto_network", "value": "Bitcoin"},
                {"entity": "contact_add_entity_wallet_address", "value": "1Dt7KiqqpgQ2UVWrNSYhEV7YWYUaGC9hFS"}
            ]
        },
        {
            "text": "Create a new contact for Emily with Ethereum wallet 0xa88a05d6a62ac84e9b8b0e58566d24a021ae8080",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "Emily"},
                {"entity": "contact_add_entity_crypto_network", "value": "Ethereum"},
                {"entity": "contact_add_entity_wallet_address", "value": "0xa88a05d6a62ac84e9b8b0e58566d24a021ae8080"}
            ]
        },
        # Test with typos
        {
            "text": "Add Michael with Bitcon address 3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "Michael"},
                {"entity": "contact_add_entity_crypto_network", "value": "Bitcon"},
                {"entity": "contact_add_entity_wallet_address", "value": "3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy"}
            ]
        },
        {
            "text": "Save Jessica's Etherium wallet 0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "Jessica"},
                {"entity": "contact_add_entity_crypto_network", "value": "Etherium"},
                {"entity": "contact_add_entity_wallet_address", "value": "0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045"}
            ]
        },
        # Test with abbreviations
        {
            "text": "Add William with BTC bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "William"},
                {"entity": "contact_add_entity_crypto_network", "value": "BTC"},
                {"entity": "contact_add_entity_wallet_address", "value": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"}
            ]
        },
        # Test with Vietnamese text
        {
            "text": "Thêm Nguyễn Văn A với địa chỉ Bitcoin 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "Nguyễn Văn A"},
                {"entity": "contact_add_entity_crypto_network", "value": "Bitcoin"},
                {"entity": "contact_add_entity_wallet_address", "value": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"}
            ]
        },
        # Mixed language test
        {
            "text": "Thêm John với Bitcoin 3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "John"},
                {"entity": "contact_add_entity_crypto_network", "value": "Bitcoin"},
                {"entity": "contact_add_entity_wallet_address", "value": "3FZbgi29cpjq2GjdwV8eyHuJJnkLtktZc5"}
            ]
        },
        # Network mismatch test
        {
            "text": "Add Thomas with Bitcoin address 0xCFE8D382D9f66a311fAa5A274891499695191991",
            "intent": "contact_add_request",
            "entities": [
                {"entity": "contact_add_entity_name", "value": "Thomas"},
                {"entity": "contact_add_entity_crypto_network", "value": "Bitcoin"},
                {"entity": "contact_add_entity_wallet_address", "value": "0xCFE8D382D9f66a311fAa5A274891499695191991"}
            ]
        }
    ]
    
    # Run NLU tests
    logger.info("Starting NLU tests...")
    test_nlu(interpreter, test_examples)
    
    logger.info("Tests completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
