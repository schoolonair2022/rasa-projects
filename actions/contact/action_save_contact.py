from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset

class ActionSaveContact(Action):
    """
    Saves a new contact to the wallet's contact list.
    This action is triggered after successfully collecting and validating all required contact information.
    """
    
    def name(self) -> Text:
        return "action_save_contact"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get all required contact information from slots
        contact_name = tracker.get_slot("contact_add_entity_name")
        crypto_network = tracker.get_slot("contact_add_entity_crypto_network")
        wallet_address = tracker.get_slot("contact_add_entity_wallet_address")
        
        # Additional validation (belt and suspenders)
        if not contact_name or not crypto_network or not wallet_address:
            dispatcher.utter_message(text="I'm missing some information needed to save this contact. Let's start over.")
            return [AllSlotsReset()]
        
        # Clean up wallet address: remove any spaces that might have been captured incorrectly
        clean_wallet_address = wallet_address.replace(" ", "")
        
        # In a real implementation, this would save to a database or API
        # For this example, we'll just log the saved contact
        print(f"Saving contact: {contact_name}, {crypto_network}, {clean_wallet_address}")
        
        # Send a confirmation message with the contact's name
        dispatcher.utter_message(text=f"Contact saved successfully! {contact_name} has been added to your wallet.")
        
        # Once saved, clear the contact-specific slots but keep some context
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