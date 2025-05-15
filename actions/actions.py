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
from rasa_sdk.events import SlotSet, AllSlotsReset, FollowupAction

class ActionValidateWalletAddress(Action):
    def name(self) -> Text:
        return "action_validate_wallet_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        wallet_address = tracker.get_slot("wallet_address")
        
        # Simple validation: EVM-like addresses start with 0x and are 42 chars long
        is_valid = False
        if wallet_address and wallet_address.startswith('0x') and len(wallet_address) == 42:
            is_valid = True
        # Add more validation for BTC, EOS addresses as needed
            
        if is_valid:
            contact_name = tracker.get_slot("contact_name")
            dispatcher.utter_message(text=f"I've added {contact_name} with address {wallet_address} to your contacts. 🎉")
            dispatcher.utter_message(text="Would you like to add a nickname or note for this contact?")
            return [SlotSet("address_valid", True)]
        else:
            dispatcher.utter_message(text="That doesn't seem to be a valid wallet address. Please check and try again.")
            return [SlotSet("address_valid", False), SlotSet("wallet_address", None)]

class ActionResetContactSlots(Action):
    def name(self) -> Text:
        return "action_reset_contact_slots"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        return [SlotSet("contact_name", None), 
                SlotSet("wallet_address", None), 
                SlotSet("network_type", None),
                SlotSet("address_valid", None)]