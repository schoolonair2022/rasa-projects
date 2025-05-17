from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActiveLoop

class ActionDeactivateLoop(Action):
    """
    Deactivates the current active form loop.
    This action is used when the form needs to be stopped due to interruptions,
    cancellations, or other exceptional circumstances.
    """
    
    def name(self) -> Text:
        return "action_deactivate_loop"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Simply deactivate any active loop
        return [ActiveLoop(None)]