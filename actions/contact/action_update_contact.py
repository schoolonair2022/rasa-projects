from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset

class ActionUpdateContact(Action):
    """
    Updates an existing contact in the wallet's contact list.
    This is triggered when a user attempts to add a contact with a name that already exists
    and confirms they want to update it.
    """
    
    def name(self) -> Text:
        return "action_update_contact"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get all required contact information from slots
        contact_name = tracker.get_slot("contact_add_entity_name")
        crypto_network = tracker.get_slot("contact_add_entity_crypto_network")
        wallet_address = tracker.get_slot("contact_add_entity_wallet_address")
        
        # Validate we have all required information
        if not contact_name or not crypto_network or not wallet_address:
            dispatcher.utter_message(text="I'm missing some information needed to update this contact. Let's start over.")
            return [AllSlotsReset()]
        
        # In a real implementation, this would update a record in a database or API
        # For this example, we'll just log the updated contact
        print(f"Updating contact: {contact_name}, {crypto_network}, {wallet_address}")
        
        # Simulate successful update
        # In a real implementation, we'd check for errors and handle them
        
        # Clear the contact-specific slots but keep some context
        return [
            SlotSet("contact_add_entity_name", None),
            SlotSet("contact_add_entity_crypto_network", None),
            SlotSet("contact_add_entity_wallet_address", None),
            SlotSet("contact_exists", False),
            SlotSet("address_valid", False),
            SlotSet("validation_attempts", 0),
            SlotSet("network_address_mismatch", False),
            SlotSet("contact_flow_active", False)
        ]