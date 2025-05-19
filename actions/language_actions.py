from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionSetVietnameseLanguage(Action):
    """Set language to Vietnamese."""

    def name(self) -> Text:
        return "action_set_vietnamese_language"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("Setting language to Vietnamese")
        
        # Respond in Vietnamese
        dispatcher.utter_message(text="Xin chào! Tôi sẽ giao tiếp với bạn bằng tiếng Việt.")
        
        # Set language slot to Vietnamese
        return [SlotSet("language", "vi")]


class ActionSetEnglishLanguage(Action):
    """Set language to English."""

    def name(self) -> Text:
        return "action_set_english_language"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        logger.info("Setting language to English")
        
        # Respond in English
        dispatcher.utter_message(text="Hello! I'll communicate with you in English.")
        
        # Set language slot to English
        return [SlotSet("language", "en")]
