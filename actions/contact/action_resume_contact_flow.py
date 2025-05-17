from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionResumeContactFlow(Action):
    """
    Resumes the contact addition flow from where it was interrupted.
    This action is called when the user wants to continue adding a contact
    after an interruption.
    """
    
    def name(self) -> Text:
        return "action_resume_contact_flow"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last active state
        last_active_state = tracker.get_slot("contact_last_active_state")
        
        # Inform the user where we're resuming from
        if last_active_state == "contact_add_entity_name":
            dispatcher.utter_message(text="Let's continue adding your contact. I'll need the contact's name.")
            
        elif last_active_state == "contact_add_entity_crypto_network":
            dispatcher.utter_message(text="Let's continue adding your contact. I'll need to know which cryptocurrency network they use.")
            
        elif last_active_state == "contact_add_entity_wallet_address":
            network = tracker.get_slot("contact_add_entity_crypto_network")
            if network:
                dispatcher.utter_message(text=f"Let's continue adding your contact. I'll need the {network} wallet address.")
            else:
                dispatcher.utter_message(text="Let's continue adding your contact. I'll need the wallet address.")
                
        else:
            # If we don't have a saved state or it's invalid, start from the beginning
            dispatcher.utter_message(text="Let's continue adding your contact. I'll guide you through the process.")
            return [SlotSet("requested_slot", "contact_add_entity_name")]
        
        # Set the requested slot back to where we left off
        return [
            SlotSet("requested_slot", last_active_state),
            SlotSet("contact_flow_active", True)
        ]