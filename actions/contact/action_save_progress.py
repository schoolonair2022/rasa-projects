from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionSaveProgress(Action):
    """
    Saves the progress of the contact addition workflow when interrupted.
    This action is called when the user wants to switch context but save their progress.
    """
    
    def name(self) -> Text:
        return "action_save_progress"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the current state of the form
        current_slot = tracker.get_slot("requested_slot")
        
        # Store the current slot as the last active state
        # This will be used when resuming the flow
        
        # Also mark the contact flow as active but interrupted
        return [
            SlotSet("contact_last_active_state", current_slot),
            SlotSet("contact_flow_active", True)
        ]