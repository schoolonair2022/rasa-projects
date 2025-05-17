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
        
        # Standardize network name (handle lowercase, abbreviations, etc.)
        network = self._standardize_network_name(crypto_network)
        
        # Validate based on network
        if network == "bitcoin":
            # Bitcoin address validation (starts with 1, 3, or bc1 and has 25-42 chars)
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
            # Litecoin address validation (typically starts with L, M, or 3)
            is_valid = self._validate_litecoin_address(wallet_address)
        
        elif network == "ripple":
            # Ripple (XRP) address validation
            is_valid = self._validate_ripple_address(wallet_address)
            
        else:
            # For other networks, use a basic length check
            is_valid = len(wallet_address) > 20  # Simplistic validation for example
        
        # Log the validation result
        print(f"Validating {network} address '{wallet_address}': {is_valid}")
        
        # Increment validation attempts
        validation_attempts += 1
        
        # Return the results
        return [
            SlotSet("address_valid", is_valid),
            SlotSet("validation_attempts", validation_attempts),
            SlotSet("network_address_mismatch", network_address_mismatch)
        ]
    
    def _standardize_network_name(self, network: str) -> str:
        """Standardize network name to handle variations and abbreviations."""
        if not network:
            return ""
            
        network = network.lower().strip()
        
        # Handle common abbreviations
        if network in ["btc", "bitcoin"]:
            return "bitcoin"
        elif network in ["eth", "ethereum"]:
            return "ethereum"
        elif network in ["ltc", "litecoin"]:
            return "litecoin"
        elif network in ["xrp", "ripple"]:
            return "ripple"
        
        return network
    
    def _validate_bitcoin_address(self, address: str) -> bool:
        """Validate Bitcoin address format."""
        # Simple regex pattern for Bitcoin addresses
        # A more robust validation would use a checksum algorithm
        pattern = r"^(1|3|bc1)[a-zA-Z0-9]{25,42}$"
        return bool(re.match(pattern, address))
    
    def _validate_ethereum_address(self, address: str) -> bool:
        """Validate Ethereum address format."""
        # Ethereum addresses are 42 characters long including the '0x' prefix
        pattern = r"^0x[a-fA-F0-9]{40}$"
        return bool(re.match(pattern, address))
    
    def _validate_litecoin_address(self, address: str) -> bool:
        """Validate Litecoin address format."""
        # Simple regex pattern for Litecoin addresses
        pattern = r"^[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$"
        return bool(re.match(pattern, address))
    
    def _validate_ripple_address(self, address: str) -> bool:
        """Validate Ripple (XRP) address format."""
        # Simple regex pattern for Ripple addresses
        pattern = r"^r[0-9a-zA-Z]{24,34}$"
        return bool(re.match(pattern, address))