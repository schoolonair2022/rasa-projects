from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionCheckContactExistence(Action):
    """
    Checks if a contact with the provided name already exists in the wallet's contact list.
    This is called during contact addition to prevent duplicate contacts.
    """
    
    def name(self) -> Text:
        return "action_check_contact_existence"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the contact name from the slot
        contact_name = tracker.get_slot("contact_add_entity_name")
        
        # If no name was provided, cannot check existence
        if not contact_name:
            return [SlotSet("contact_exists", False)]
        
        # In a real implementation, this would query a database or API
        # Here we'll simulate with a list of existing contacts
        existing_contacts = [
            "John Smith", 
            "Sarah Johnson", 
            "Sophia Miller", 
            "William Jones"
            # Add other sample names for testing
        ]
        
        # Check if the contact name exists (case-insensitive)
        contact_exists = any(existing.lower() == contact_name.lower() for existing in existing_contacts)
        
        # Log the result for debugging
        print(f"Checking if contact '{contact_name}' exists: {contact_exists}")
        
        # Return the result as a slot
        return [SlotSet("contact_exists", contact_exists)]