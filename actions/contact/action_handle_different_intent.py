from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActionExecuted

class ActionHandleDifferentIntent(Action):
    """
    Handles the transition when a user expresses a different intent during contact addition.
    This action helps manage context switching while preserving the contact addition state.
    """
    
    def name(self) -> Text:
        return "action_handle_different_intent"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the latest intent that caused the interruption
        latest_intent = None
        for event in reversed(tracker.events):
            if event.get("event") == "user" and event.get("parse_data"):
                latest_intent = event.get("parse_data").get("intent", {}).get("name")
                break
        
        # Set up context marker to help the conversation resume later
        # Save the form state
        form_state = {
            "contact_add_entity_name": tracker.get_slot("contact_add_entity_name"),
            "contact_add_entity_crypto_network": tracker.get_slot("contact_add_entity_crypto_network"),
            "contact_add_entity_wallet_address": tracker.get_slot("contact_add_entity_wallet_address"),
            "requested_slot": tracker.get_slot("requested_slot")
        }
        
        # Let the user know we're switching contexts
        dispatcher.utter_message(text=f"I'll help you with that. We'll come back to adding the contact afterward if you'd like.")
        
        # Return events to set up the context switch
        return [
            SlotSet("previous_context", "add_contact"),
            SlotSet("previous_form_state", str(form_state)),
            SlotSet("contact_flow_active", True),
            # Trigger the appropriate action for the new intent if we identified it
            # This would be implemented based on your specific bot's capabilities
            # For example: ActionExecuted(f"utter_{latest_intent}") if it exists
        ]