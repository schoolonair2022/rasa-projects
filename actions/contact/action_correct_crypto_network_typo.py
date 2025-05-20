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

class ActionCorrectCryptoNetworkTypo(Action):
    """
    Attempts to correct common typos in cryptocurrency network names.
    This improves user experience by handling minor spelling errors gracefully.
    """
    
    def name(self) -> Text:
        return "action_correct_crypto_network_typo"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the original network name with potential typo
        network_with_typo = tracker.get_slot("contact_add_entity_crypto_network")
        
        if not network_with_typo:
            return []
        
        # Clean up any JSON or formatting artifacts that might be in the network name
        # This handles cases like '"Bitcoin"}' or other formatting issues
        cleaned_network = re.sub(r'["\'\{\}]', '', network_with_typo).strip()
        
        logger.info(f"Cleaning network name from '{network_with_typo}' to '{cleaned_network}'")
        
        # List of known cryptocurrency networks (comprehensive list)
        known_networks = [
            "Bitcoin", "Ethereum", "Litecoin", "Ripple", "Dogecoin", 
            "Bitcoin Cash", "Stellar", "Cardano", "Polkadot", "Solana",
            "Avalanche", "USD Coin", "Tether", "Binance Coin", "Chainlink",
            "Monero", "Cosmos", "Uniswap", "Polygon", "Algorand",
            "Near Protocol", "VeChain", "Tron", "EOS", "Filecoin",
            "Aave", "Tezos", "Maker", "Neo", "Stacks"
        ]
        
        # Dictionary to map abbreviations to full names
        abbrev_to_full = {
            "BTC": "Bitcoin", "ETH": "Ethereum", "LTC": "Litecoin", 
            "XRP": "Ripple", "DOGE": "Dogecoin", "BCH": "Bitcoin Cash", 
            "XLM": "Stellar", "ADA": "Cardano", "DOT": "Polkadot", 
            "SOL": "Solana", "AVAX": "Avalanche", "USDC": "USD Coin", 
            "USDT": "Tether", "BNB": "Binance Coin", "LINK": "Chainlink",
            "XMR": "Monero", "ATOM": "Cosmos", "UNI": "Uniswap", 
            "MATIC": "Polygon", "ALGO": "Algorand", "NEAR": "Near Protocol", 
            "VET": "VeChain", "TRX": "Tron", "EOS": "EOS", 
            "FIL": "Filecoin", "AAVE": "Aave", "XTZ": "Tezos", 
            "MKR": "Maker", "NEO": "Neo", "STX": "Stacks"
        }
        
        # Check if the cleaned network name is already a valid network
        if cleaned_network in known_networks:
            logger.info(f"Cleaned network '{cleaned_network}' is already a valid network")
            return [
                SlotSet("contact_add_entity_crypto_network", cleaned_network),
                SlotSet("crypto_network_typo", False)
            ]
        
        # Check if it's a known abbreviation (case insensitive)
        upper_network = cleaned_network.upper()
        if upper_network in abbrev_to_full:
            corrected_network = abbrev_to_full[upper_network]
            logger.info(f"Converting abbreviation '{cleaned_network}' to '{corrected_network}'")
            dispatcher.utter_message(text=f"I'll use {corrected_network} as the cryptocurrency network.")
            return [
                SlotSet("contact_add_entity_crypto_network", corrected_network),
                SlotSet("crypto_network_typo", False)  # Not actually a typo, just an abbreviation
            ]
        
        # All networks including abbreviations for fuzzy matching
        all_networks = known_networks + list(abbrev_to_full.keys())
        
        # Find closest match to correct typos
        closest_match = difflib.get_close_matches(cleaned_network, all_networks, n=1, cutoff=0.6)
        
        if closest_match:
            match = closest_match[0]
            
            # If we matched an abbreviation, convert to full name for consistency
            if match in abbrev_to_full:
                corrected_network = abbrev_to_full[match]
            else:
                corrected_network = match
            
            logger.info(f"Corrected network from '{cleaned_network}' to '{corrected_network}'")
            
            # Inform the user about the correction
            dispatcher.utter_message(text=f"I'll use {corrected_network} as the cryptocurrency network.")
            
            # Return the corrected network and set the typo flag
            return [
                SlotSet("contact_add_entity_crypto_network", corrected_network),
                SlotSet("crypto_network_typo", True)
            ]
        
        # If no close match, don't change the value but use the cleaned version
        logger.info(f"No close match found for '{cleaned_network}', using cleaned version")
        return [
            SlotSet("contact_add_entity_crypto_network", cleaned_network),
            SlotSet("crypto_network_typo", False)
        ]