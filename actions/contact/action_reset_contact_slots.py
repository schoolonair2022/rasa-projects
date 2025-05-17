from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionResetContactSlots(Action):
    """
    Resets all slots related to contact addition.
    This is used when cancelling the contact addition process or after
    completing a contact addition to prepare for the next operation.
    """
    
    def name(self) -> Text:
        return "action_reset_contact_slots"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Reset all slots related to contact addition
        return [
            SlotSet("contact_add_entity_name", None),
            SlotSet("contact_add_entity_crypto_network", None),
            SlotSet("contact_add_entity_wallet_address", None),
            SlotSet("contact_exists", False),
            SlotSet("address_valid", False),
            SlotSet("validation_attempts", 0),
            SlotSet("network_address_mismatch", False),
            SlotSet("multiple_networks_detected", False),
            SlotSet("unsupported_cryptocurrency", False),
            SlotSet("contact_flow_active", False),
            SlotSet("contact_last_active_state", None)
        ]