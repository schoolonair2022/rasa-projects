from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import difflib
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionCheckContactExistence(Action):
    """
    Checks if a contact with the provided name already exists in the wallet's contact list.
    This is called during contact addition to prevent duplicate contacts.
    Also detects if there's a typo in the crypto network name.
    """
    
    def name(self) -> Text:
        return "action_check_contact_existence"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the contact name from the slot
        contact_name = tracker.get_slot("contact_add_entity_name")
        
        # If no name was provided, cannot check existence
        if not contact_name:
            return [SlotSet("contact_exists", False)]
        
        # In a real implementation, this would query a database or API
        # Here we'll simulate with a list of existing contacts
        existing_contacts = [
            "John Smith", 
            "Sarah Johnson", 
            "Sophia Miller", 
            "William Jones"
            # Add other sample names for testing
        ]
        
        # Check if the contact name exists (case-insensitive)
        contact_exists = any(existing.lower() == contact_name.lower() for existing in existing_contacts)
        
        # Log the result for debugging
        logger.info(f"Checking if contact '{contact_name}' exists: {contact_exists}")
        
        # Now also check if there might be a typo in the crypto network name
        network_name = tracker.get_slot("contact_add_entity_crypto_network")
        crypto_network_typo = False
        
        if network_name:
            # Clean up any JSON or formatting artifacts that might be in the network name
            # This handles cases like '"Bitcoin"}' or other formatting issues
            cleaned_network = re.sub(r'["\'\{\}]', '', network_name).strip()
            
            logger.info(f"Checking crypto network. Original: '{network_name}', Cleaned: '{cleaned_network}'")
            
            # List of known cryptocurrency networks (comprehensive list)
            known_networks = [
                "Bitcoin", "Ethereum", "Litecoin", "Ripple", "Dogecoin", 
                "Bitcoin Cash", "Stellar", "Cardano", "Polkadot", "Solana",
                "Avalanche", "USD Coin", "Tether", "Binance Coin", "Chainlink",
                "Monero", "Cosmos", "Uniswap", "Polygon", "Algorand",
                "Near Protocol", "VeChain", "Tron", "EOS", "Filecoin",
                "Aave", "Tezos", "Maker", "Neo", "Stacks"
            ]
            
            # Also include common abbreviations
            abbrevs = ["BTC", "ETH", "LTC", "XRP", "DOGE", "BCH", "XLM", "ADA", 
                      "DOT", "SOL", "AVAX", "USDC", "USDT", "BNB", "LINK", 
                      "XMR", "ATOM", "UNI", "MATIC", "ALGO", "NEAR", "VET", 
                      "TRX", "EOS", "FIL", "AAVE", "XTZ", "MKR", "NEO", "STX"]
            
            all_networks = known_networks + abbrevs
            
            # Check if the cleaned network name is a valid network (exact match)
            if cleaned_network in all_networks:
                logger.info(f"'{cleaned_network}' is a valid network name")
                # If the network name needed cleaning but is valid, we'll still need to update it
                if cleaned_network != network_name:
                    return [
                        SlotSet("contact_exists", contact_exists),
                        SlotSet("contact_add_entity_crypto_network", cleaned_network),
                        SlotSet("crypto_network_typo", False)
                    ]
                # Otherwise, it's already correct
                return [
                    SlotSet("contact_exists", contact_exists),
                    SlotSet("crypto_network_typo", False)
                ]
            
            # If not an exact match, check for a close match (typo)
            closest_match = difflib.get_close_matches(cleaned_network, all_networks, n=1, cutoff=0.6)
            if closest_match:
                crypto_network_typo = True
                logger.info(f"Detected typo in '{cleaned_network}'. Closest match: '{closest_match[0]}'")
        
        # Return the contact existence result and typo detection
        return [
            SlotSet("contact_exists", contact_exists),
            SlotSet("crypto_network_typo", crypto_network_typo)
        ]