# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, AllSlotsReset, FollowupAction

import logging
from . import utils

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Validating wallet address: {wallet_address}")
        
        network_type = None
        is_valid = False
        
        if wallet_address:
            # Use the validation utility from utils.py
            is_valid, detected_network = utils.validate_crypto_address(wallet_address)
            if is_valid:
                network_type = detected_network
                logger.info(f"Address {wallet_address} validated as {network_type} address")
            
        if is_valid:
            contact_name = tracker.get_slot("contact_name")
            network_info = f" ({network_type})" if network_type else ""
            dispatcher.utter_message(text=f"I've added {contact_name} with address {wallet_address}{network_info} to your contacts. 🎉")
            dispatcher.utter_message(text="Would you like to add a nickname or note for this contact?")
            return [SlotSet("address_valid", True), SlotSet("network_type", network_type)]
        else:
            dispatcher.utter_message(text="That doesn't seem to be a valid wallet address. Please check and try again.")
            return [SlotSet("address_valid", False)]

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