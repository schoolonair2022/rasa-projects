# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset

class ActionValidateWalletAddress(Action):
    def name(self) -> Text:
        return "action_validate_wallet_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        wallet_address = tracker.get_slot("wallet_address")
        
        # This is a simple validation for demonstration
        # In a real application, you would use web3 libraries or API calls to validate
        is_valid = False
        
        # Simple validation: EVM-like addresses start with 0x and are 42 chars long
        if wallet_address and wallet_address.startswith('0x') and len(wallet_address) == 42:
            is_valid = True
        # Add more validation for BTC, EOS addresses as needed
            
        if is_valid:
            return []
        else:
            dispatcher.utter_message(template="utter_add_contact_invalid_address")
            return [SlotSet("wallet_address", None)]

class ActionResetContactSlots(Action):
    def name(self) -> Text:
        return "action_reset_contact_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("contact_name", None), SlotSet("wallet_address", None), SlotSet("network_type", None)]