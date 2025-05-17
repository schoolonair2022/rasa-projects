from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionOfferValidationAlternatives(Action):
    """
    Offers alternatives when wallet address validation fails multiple times.
    This provides users with helpful guidance after several failed attempts.
    """
    
    def name(self) -> Text:
        return "action_offer_validation_alternatives"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the cryptocurrency network to provide network-specific help
        network = tracker.get_slot("contact_add_entity_crypto_network")
        
        # Default network if none specified
        if not network:
            network = "cryptocurrency"
        
        # Offer options based on network
        message = (
            f"I notice you're having trouble providing a valid {network} address. Here are some suggestions:\n\n"
            f"1. Double-check the address for any typos or missing characters.\n"
            f"2. Make sure you've selected the correct network ({network}).\n"
            f"3. Copy and paste the address directly from your source to avoid errors.\n"
            f"4. Check if the address is for a different network than {network}.\n\n"
            f"Would you like me to show you an example of a valid {network} address format?"
        )
        
        dispatcher.utter_message(text=message)
        
        # No changes to slots
        return []