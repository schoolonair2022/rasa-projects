from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import difflib

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
            return [
                SlotSet("unsupported_cryptocurrency", False),
                SlotSet("crypto_network_typo", False)
            ]
        
        # Reset typo flag - it should be set by action_check_contact_existence and action_correct_crypto_network_typo
        events = [SlotSet("crypto_network_typo", False)]
        
        # Standardize network name (lowercase and handle abbreviations)
        network, has_typo = self._standardize_network_name(crypto_network)
        
        # List of supported cryptocurrencies (expanded)
        supported_networks = [
            "bitcoin", "ethereum", "litecoin", "ripple", "dogecoin", 
            "bitcoin cash", "stellar", "cardano", "polkadot", "solana",
            "avalanche", "usd coin", "tether", "binance coin", "chainlink",
            "polygon", "near", "algorand", "cosmos", "tezos",
            "binance smart chain", "monero", "tron", "eos", "filecoin",
            "decentraland", "uniswap", "aave", "compound", "terraform labs",
            "the graph", "hedera hashgraph", "fantom", "vechain", "theta",
            "harmony"
        ]
        
        # Check if the network is supported
        is_supported = network in supported_networks
        
        # If there appears to be a typo, try to find the closest match
        if not is_supported and has_typo:
            closest_match = self._find_closest_match(network, supported_networks)
            if closest_match:
                # If we have a close match above similarity threshold, assume a typo
                events.append(SlotSet("crypto_network_typo", True))
                network = closest_match
                is_supported = True
                print(f"Corrected network typo from '{crypto_network}' to '{self._format_network_name(network)}'")
        
        # If it's a supported network, update the slot with the standardized name
        if is_supported:
            events.extend([
                SlotSet("contact_add_entity_crypto_network", self._format_network_name(network)),
                SlotSet("unsupported_cryptocurrency", False)
            ])
        else:
            # If not supported, set the flag but keep the original input
            # This allows the chatbot to ask for clarification
            events.append(SlotSet("unsupported_cryptocurrency", True))
            print(f"Unsupported cryptocurrency: {crypto_network}")
        
        return events
    
    def _standardize_network_name(self, network: str) -> tuple:
        """Standardize network name to handle variations and abbreviations."""
        if not network:
            return "", False
            
        network = network.lower().strip()
        has_typo = False
        
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
            "bsc": "binance smart chain",
            "binance smart chain": "binance smart chain",
            "link": "chainlink",
            "chainlink": "chainlink",
            "matic": "polygon",
            "polygon": "polygon",
            "near": "near",
            "algo": "algorand",
            "algorand": "algorand",
            "atom": "cosmos",
            "cosmos": "cosmos",
            "xtz": "tezos",
            "tezos": "tezos",
            "uniswap": "uniswap",
            "uni": "uniswap",
            "aave": "aave",
            "comp": "compound",
            "compound": "compound",
            "xmr": "monero",
            "monero": "monero",
            "trx": "tron",
            "tron": "tron"
        }
        
        # Check if network is in the mapping
        if network in network_mapping:
            return network_mapping[network], False
        
        # Check for common typo variations not in the direct mapping
        typo_variations = {
            "bitcon": "bitcoin",
            "bitcooin": "bitcoin",
            "bitcion": "bitcoin",
            "bitoin": "bitcoin",
            "etherium": "ethereum",
            "etherum": "ethereum",
            "etherem": "ethereum",
            "ethreum": "ethereum",
            "literium": "litecoin",
            "litecione": "litecoin",
            "doogecoin": "dogecoin",
            "dodgecoin": "dogecoin",
            "dogecione": "dogecoin",
            "rippl": "ripple",
            "riple": "ripple",
            "solona": "solana",
            "selena": "solana",
            "selenum": "solana",
            "cardeno": "cardano",
            "cardona": "cardano",
            "avalanch": "avalanche",
            "avalence": "avalanche",
            "polkadot": "polkadot",
            "polygone": "polygon",
            "poligon": "polygon"
        }
        
        if network in typo_variations:
            return typo_variations[network], True
            
        # If not found in mappings, return as is
        return network, False
    
    def _find_closest_match(self, input_network: str, supported_networks: list, threshold: float = 0.75) -> str:
        """Find the closest matching network name above a threshold."""
        closest_match = ""
        highest_similarity = 0
        
        for network in supported_networks:
            # Use SequenceMatcher to compare strings
            similarity = difflib.SequenceMatcher(None, input_network, network).ratio()
            
            if similarity > highest_similarity and similarity >= threshold:
                highest_similarity = similarity
                closest_match = network
        
        return closest_match
    
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
            "binance smart chain": "Binance Smart Chain (BSC)",
            "chainlink": "Chainlink",
            "polygon": "Polygon (MATIC)",
            "near": "NEAR Protocol",
            "algorand": "Algorand",
            "cosmos": "Cosmos",
            "tezos": "Tezos",
            "monero": "Monero",
            "tron": "TRON",
            "uniswap": "Uniswap",
            "aave": "Aave",
            "compound": "Compound",
            "vechain": "VeChain",
            "filecoin": "Filecoin",
            "hedera hashgraph": "Hedera Hashgraph",
            "the graph": "The Graph",
            "fantom": "Fantom",
            "harmony": "Harmony",
            "eos": "EOS"
        }
        
        # Return the formatted name or default to title case
        return formatting_map.get(network, network.title())