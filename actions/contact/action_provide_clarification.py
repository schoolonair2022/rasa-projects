from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

class ActionProvideClarification(Action):
    """
    Provides clarification about the current step in the contact addition process.
    Responds to user questions like "What do you mean?" or "I don't understand."
    """
    
    def name(self) -> Text:
        return "action_provide_clarification"
        
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Determine what slot is currently being requested to provide specific help
        requested_slot = tracker.get_slot("requested_slot")
        
        if requested_slot == "contact_add_entity_name":
            dispatcher.utter_message(text="I need a name to identify this contact in your wallet. This can be any name you'll recognize, like 'John Smith' or 'Coffee Shop'.")
            
        elif requested_slot == "contact_add_entity_crypto_network":
            dispatcher.utter_message(text="I need to know which cryptocurrency network this contact uses. For example, 'Bitcoin', 'Ethereum', or 'Litecoin'. This is important because each network has different address formats.")
            
        elif requested_slot == "contact_add_entity_wallet_address":
            # Get the network to provide network-specific help
            network = tracker.get_slot("contact_add_entity_crypto_network")
            
            if network and network.lower() in ["bitcoin", "btc"]:
                dispatcher.utter_message(text="I need the Bitcoin wallet address for this contact. Bitcoin addresses are typically 26-35 characters long and start with 1, 3, or bc1. For example: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
            
            elif network and network.lower() in ["ethereum", "eth"]:
                dispatcher.utter_message(text="I need the Ethereum wallet address for this contact. Ethereum addresses are 42 characters long and start with '0x'. For example: 0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
            
            else:
                dispatcher.utter_message(text="I need the wallet address for this contact. This is a unique alphanumeric string that identifies their wallet on the blockchain.")
            
        else:
            # General clarification if we're not in a specific slot-filling step
            dispatcher.utter_message(text="I'm helping you add a new contact to your cryptocurrency wallet. I'll need the contact's name, the cryptocurrency network they use, and their wallet address.")
        
        # No need to modify any slots
        return []