from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import difflib

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
        print(f"Checking if contact '{contact_name}' exists: {contact_exists}")
        
        # Now also check if there might be a typo in the crypto network name
        network_name = tracker.get_slot("contact_add_entity_crypto_network")
        crypto_network_typo = False
        
        if network_name:
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
            
            # First check if the exact name is in the list
            if network_name not in all_networks:
                # If not, check if there's a close match (indicating a typo)
                closest_match = difflib.get_close_matches(network_name, all_networks, n=1, cutoff=0.6)
                if closest_match:
                    crypto_network_typo = True
                    print(f"Detected typo in '{network_name}'. Closest match: '{closest_match[0]}'")
        
        # Return the contact existence result and typo detection
        return [
            SlotSet("contact_exists", contact_exists),
            SlotSet("crypto_network_typo", crypto_network_typo)
        ]