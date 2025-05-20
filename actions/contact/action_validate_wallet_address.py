import re
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionValidateWalletAddress(Action):
    """
    Validates the provided wallet address based on the cryptocurrency network.
    Each cryptocurrency has its own address format requirements.
    """
    
    def name(self) -> Text:
        return "action_validate_wallet_address"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the necessary slots
        wallet_address = tracker.get_slot("contact_add_entity_wallet_address")
        crypto_network = tracker.get_slot("contact_add_entity_crypto_network")
        
        # Get current validation attempts
        validation_attempts = tracker.get_slot("validation_attempts") or 0
        
        # Default return values
        is_valid = False
        network_address_mismatch = False
        
        # If we don't have both needed values, we can't validate
        if not wallet_address or not crypto_network:
            return [
                SlotSet("address_valid", False),
                SlotSet("validation_attempts", validation_attempts + 1),
                SlotSet("network_address_mismatch", False)
            ]

        # Clean up wallet address: remove any spaces that might have been captured incorrectly
        wallet_address = wallet_address.replace(" ", "")
        
        # Standardize network name (handle lowercase, abbreviations, etc.)
        network = self._standardize_network_name(crypto_network)
        
        # Validate based on network
        if network == "bitcoin":
            # Bitcoin address validation (Legacy, SegWit, and Bech32 formats)
            is_valid = self._validate_bitcoin_address(wallet_address)
            # Check if this looks like an Ethereum address instead
            if not is_valid and wallet_address.startswith("0x"):
                network_address_mismatch = True
                
        elif network == "ethereum":
            # Ethereum address validation (starts with 0x and has 42 chars)
            is_valid = self._validate_ethereum_address(wallet_address)
            # Check if this looks like a Bitcoin address instead
            if not is_valid and (wallet_address.startswith("1") or wallet_address.startswith("3") or wallet_address.startswith("bc1")):
                network_address_mismatch = True
                
        elif network == "litecoin":
            # Litecoin address validation (starts with L, M, 3, or ltc1)
            is_valid = self._validate_litecoin_address(wallet_address)
        
        elif network == "ripple" or network == "xrp":
            # Ripple (XRP) address validation
            is_valid = self._validate_ripple_address(wallet_address)
            
        elif network == "solana" or network == "sol":
            # Solana address validation (base58 encoded, 32-44 chars)
            is_valid = self._validate_solana_address(wallet_address)
            
        elif network == "cardano" or network == "ada":
            # Cardano address validation (starts with addr1, ~ 100 chars)
            is_valid = self._validate_cardano_address(wallet_address)
            
        elif network == "dogecoin" or network == "doge":
            # Dogecoin address validation (starts with D, usually 34 chars)
            is_valid = self._validate_dogecoin_address(wallet_address)
            
        elif network == "polkadot" or network == "dot":
            # Polkadot address validation (starts with 1, usually 48 chars)
            is_valid = self._validate_polkadot_address(wallet_address)
            
        elif network == "near":
            # NEAR address validation (account name format)
            is_valid = self._validate_near_address(wallet_address)
            
        elif network in ["binance smart chain", "bsc", "binance coin", "bnb"]:
            # BSC uses same format as Ethereum (0x...)
            is_valid = self._validate_ethereum_address(wallet_address)
            
        else:
            # For other networks, use a more permissive check
            # At minimum, address should be at least 20 chars long
            is_valid = len(wallet_address) >= 20
        
        # Log the validation result
        print(f"Validating {network} address '{wallet_address}': {is_valid}")
        
        # Increment validation attempts
        validation_attempts += 1
        
        # Return the results
        return [
            SlotSet("address_valid", is_valid),
            SlotSet("validation_attempts", validation_attempts),
            SlotSet("network_address_mismatch", network_address_mismatch),
            SlotSet("contact_add_entity_wallet_address", wallet_address)  # Store the cleaned address
        ]
    
    def _standardize_network_name(self, network: str) -> str:
        """Standardize network name to handle variations and abbreviations."""
        if not network:
            return ""
            
        network = network.lower().strip()
        
        # Handle common abbreviations and variants with typos
        network_mapping = {
            "btc": "bitcoin",
            "bitcoin": "bitcoin",
            "bitcon": "bitcoin",
            "bitcoincash": "bitcoin cash",
            "bit coin": "bitcoin",
            "eth": "ethereum",
            "ethereum": "ethereum", 
            "etherium": "ethereum",
            "etherem": "ethereum",
            "etherum": "ethereum",
            "ltc": "litecoin",
            "litecoin": "litecoin",
            "xrp": "ripple",
            "ripple": "ripple",
            "doge": "dogecoin",
            "dogecoin": "dogecoin",
            "dodge": "dogecoin",
            "dogcoin": "dogecoin",
            "bnb": "binance coin",
            "binance coin": "binance coin",
            "binance": "binance coin",
            "binance smart chain": "binance smart chain",
            "bsc": "binance smart chain",
            "sol": "solana",
            "solana": "solana",
            "ada": "cardano",
            "cardano": "cardano",
            "cardeno": "cardano",
            "dot": "polkadot",
            "polkadot": "polkadot",
            "near": "near",
            "avax": "avalanche",
            "avalanche": "avalanche",
            "usdt": "tether",
            "tether": "tether",
            "usdc": "usd coin",
            "usd coin": "usd coin",
            "matic": "polygon",
            "polygon": "polygon",
            "link": "chainlink",
            "chainlink": "chainlink"
        }
        
        return network_mapping.get(network, network)
    
    def _validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address format."""
        # Legacy, SegWit, and Bech32 formats
        pattern = r"^(1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-Z0-9]{25,90})$"
        return bool(re.match(pattern, address))
    
    def _validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address format."""
        # Ethereum addresses are 42 characters long including the '0x' prefix
        pattern = r"^0x[a-fA-F0-9]{40}$"
        return bool(re.match(pattern, address))
    
    def _validate_litecoin_address(self, address: str) -> bool:
        """Validate Litecoin address format."""
        # Legacy, SegWit, and Bech32 formats for Litecoin
        pattern = r"^([LM3][a-km-zA-HJ-NP-Z1-9]{26,33}|ltc1[a-zA-Z0-9]{25,90})$"
        return bool(re.match(pattern, address))
    
    def _validate_ripple_address(self, address: str) -> bool:
        """Validate Ripple (XRP) address format."""
        # Simple regex pattern for Ripple addresses
        pattern = r"^r[0-9a-zA-Z]{24,34}$"
        return bool(re.match(pattern, address))
    
    def _validate_solana_address(self, address: str) -> bool:
        """Validate Solana address format."""
        # Base58 encoded, usually 32-44 characters
        pattern = r"^[1-9A-HJ-NP-Za-km-z]{32,44}$"
        return bool(re.match(pattern, address))
    
    def _validate_cardano_address(self, address: str) -> bool:
        """Validate Cardano address format."""
        # Starts with addr1 and is about 100 characters long
        pattern = r"^addr1[a-zA-Z0-9]{90,110}$"
        return bool(re.match(pattern, address))
    
    def _validate_dogecoin_address(self, address: str) -> bool:
        """Validate Dogecoin address format."""
        # Starts with D and is typically 34 characters
        pattern = r"^D[a-km-zA-HJ-NP-Z1-9]{25,34}$"
        return bool(re.match(pattern, address))
    
    def _validate_polkadot_address(self, address: str) -> bool:
        """Validate Polkadot address format."""
        # Usually starts with 1 and is 48 characters long
        pattern = r"^1[a-zA-Z0-9]{47,48}$"
        return bool(re.match(pattern, address))
    
    def _validate_near_address(self, address: str) -> bool:
        """Validate NEAR address format."""
        # NEAR uses account names ending with .near
        pattern = r"^[a-z0-9_-]{2,64}\.near$"
        return bool(re.match(pattern, address))