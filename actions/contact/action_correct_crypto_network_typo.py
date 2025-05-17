from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import difflib

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
        
        # Find closest match to correct typos
        closest_match = difflib.get_close_matches(network_with_typo, all_networks, n=1, cutoff=0.6)
        
        if closest_match:
            corrected_network = closest_match[0]
            
            # If we matched an abbreviation, convert to full name for consistency
            if corrected_network in abbrevs:
                idx = abbrevs.index(corrected_network)
                corrected_network = known_networks[idx % len(known_networks)]
            
            # Inform the user about the correction
            dispatcher.utter_message(text=f"I'll use {corrected_network} as the cryptocurrency network.")
            
            # Return the corrected network
            return [SlotSet("contact_add_entity_crypto_network", corrected_network)]
        
        # If no close match, don't change the value
        return []