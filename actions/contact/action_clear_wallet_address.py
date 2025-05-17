from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionClearWalletAddress(Action):
    """
    Clears only the wallet address slot.
    Used when there's a network/address mismatch to let the user try again.
    """
    
    def name(self) -> Text:
        return "action_clear_wallet_address"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Clear just the wallet address slot
        return [
            SlotSet("contact_add_entity_wallet_address", None),
            SlotSet("address_valid", False),
            SlotSet("network_address_mismatch", False),
            # Reset the validation attempts counter
            SlotSet("validation_attempts", 0)
        ]