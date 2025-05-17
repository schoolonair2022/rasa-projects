from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionGoBackInForm(Action):
    """
    Allows the user to go back to the previous question in the form.
    This provides flexibility when users want to change previously provided information.
    """
    
    def name(self) -> Text:
        return "action_go_back_in_form"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get current requested slot
        current_slot = tracker.get_slot("requested_slot")
        
        # Determine which slot to go back to
        if current_slot == "contact_add_entity_wallet_address":
            # Go back to network selection
            dispatcher.utter_message(text="Let's go back to selecting the cryptocurrency network.")
            return [SlotSet("requested_slot", "contact_add_entity_crypto_network")]
            
        elif current_slot == "contact_add_entity_crypto_network":
            # Go back to contact name
            dispatcher.utter_message(text="Let's go back to entering the contact name.")
            return [SlotSet("requested_slot", "contact_add_entity_name")]
            
        else:
            # Can't go back further or not in a form
            dispatcher.utter_message(text="We're at the beginning of the process. Let's continue from here.")
            return []