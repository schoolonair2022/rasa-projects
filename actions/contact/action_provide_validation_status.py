from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionProvideValidationStatus(Action):
    """
    Provides information about the current validation status of the contact.
    Used when users ask if their information is valid or about the progress.
    """
    
    def name(self) -> Text:
        return "action_provide_validation_status"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get slot values
        name = tracker.get_slot("contact_add_entity_name")
        network = tracker.get_slot("contact_add_entity_crypto_network")
        address = tracker.get_slot("contact_add_entity_wallet_address")
        address_valid = tracker.get_slot("address_valid")
        
        # Prepare status message
        status_parts = []
        
        if name:
            status_parts.append(f"✓ Contact name: {name}")
        else:
            status_parts.append("❌ Contact name: Not provided")
            
        if network:
            status_parts.append(f"✓ Cryptocurrency network: {network}")
        else:
            status_parts.append("❌ Cryptocurrency network: Not provided")
            
        if address:
            if address_valid:
                status_parts.append(f"✓ Wallet address: Valid")
            else:
                status_parts.append(f"❌ Wallet address: Invalid format")
        else:
            status_parts.append("❌ Wallet address: Not provided")
            
        # Create and send the status message
        status_message = "Here's your current contact validation status:\n\n" + "\n".join(status_parts)
        
        # Add a summary
        if name and network and address and address_valid:
            status_message += "\n\nAll information is valid and ready to save."
        else:
            status_message += "\n\nSome information is still needed or invalid."
            
        dispatcher.utter_message(text=status_message)
        
        # No changes to slots
        return []