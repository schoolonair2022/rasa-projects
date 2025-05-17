from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionClearCryptoNetwork(Action):
    """
    Clears only the cryptocurrency network slot.
    Used when the user selects an unsupported cryptocurrency.
    """
    
    def name(self) -> Text:
        return "action_clear_crypto_network"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Clear just the crypto network slot
        return [
            SlotSet("contact_add_entity_crypto_network", None),
            SlotSet("unsupported_cryptocurrency", False),
            # Also clear wallet address since it would be invalid with a different network
            SlotSet("contact_add_entity_wallet_address", None),
            SlotSet("address_valid", False),
            SlotSet("validation_attempts", 0)
        ]