from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionValidateCryptoNetwork(Action):
    """
    Validates the cryptocurrency network provided by the user.
    Checks if the network is supported and standardizes network names.
    """
    
    def name(self) -> Text:
        return "action_validate_crypto_network"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the provided crypto network
        crypto_network = tracker.get_slot("contact_add_entity_crypto_network")
        
        if not crypto_network:
            return [SlotSet("unsupported_cryptocurrency", False)]
        
        # Standardize network name (lowercase and handle abbreviations)
        network = self._standardize_network_name(crypto_network)
        
        # List of supported cryptocurrencies
        supported_networks = [
            "bitcoin", "ethereum", "litecoin", "ripple", "dogecoin", 
            "bitcoin cash", "stellar", "cardano", "polkadot", "solana",
            "avalanche", "usd coin", "tether", "binance coin", "chainlink"
        ]
        
        # Check if the network is supported
        is_supported = network in supported_networks
        
        # If it's a supported network, update the slot with the standardized name
        if is_supported:
            return [
                SlotSet("contact_add_entity_crypto_network", self._format_network_name(network)),
                SlotSet("unsupported_cryptocurrency", False)
            ]
        else:
            # If not supported, set the flag
            return [
                SlotSet("unsupported_cryptocurrency", True)
            ]
    
    def _standardize_network_name(self, network: str) -> str:
        """Standardize network name to handle variations and abbreviations."""
        if not network:
            return ""
            
        network = network.lower().strip()
        
        # Handle common abbreviations and variations
        network_mapping = {
            "btc": "bitcoin",
            "bitcoin": "bitcoin",
            "eth": "ethereum",
            "ethereum": "ethereum",
            "ltc": "litecoin",
            "litecoin": "litecoin",
            "xrp": "ripple",
            "ripple": "ripple",
            "doge": "dogecoin", 
            "dogecoin": "dogecoin",
            "bch": "bitcoin cash",
            "bitcoin cash": "bitcoin cash",
            "xlm": "stellar",
            "stellar": "stellar",
            "ada": "cardano",
            "cardano": "cardano",
            "dot": "polkadot",
            "polkadot": "polkadot",
            "sol": "solana",
            "solana": "solana",
            "avax": "avalanche",
            "avalanche": "avalanche",
            "usdc": "usd coin",
            "usd coin": "usd coin",
            "usdt": "tether",
            "tether": "tether",
            "bnb": "binance coin",
            "binance coin": "binance coin",
            "link": "chainlink",
            "chainlink": "chainlink"
        }
        
        return network_mapping.get(network, network)
    
    def _format_network_name(self, network: str) -> str:
        """Format network name for display with proper capitalization."""
        if not network:
            return ""
            
        # Proper formatting for display
        formatting_map = {
            "bitcoin": "Bitcoin",
            "ethereum": "Ethereum",
            "litecoin": "Litecoin",
            "ripple": "Ripple (XRP)",
            "dogecoin": "Dogecoin",
            "bitcoin cash": "Bitcoin Cash",
            "stellar": "Stellar",
            "cardano": "Cardano",
            "polkadot": "Polkadot",
            "solana": "Solana",
            "avalanche": "Avalanche",
            "usd coin": "USD Coin (USDC)",
            "tether": "Tether (USDT)",
            "binance coin": "Binance Coin (BNB)",
            "chainlink": "Chainlink"
        }
        
        return formatting_map.get(network, network.title())