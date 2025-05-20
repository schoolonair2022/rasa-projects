from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SessionStarted, ActionExecuted, UserUtteranceReverted

class ActionSessionStart(Action):
    """Action to run at the start of a session."""

    def name(self) -> Text:
        return "action_session_start"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Initialize session
        events = [SessionStarted()]
        
        # The following ensures initial action listen is logged
        events.append(ActionExecuted("action_listen"))
        
        return events

class ActionDefaultFallback(Action):
    """Default fallback action when the bot doesn't know how to respond."""

    def name(self) -> Text:
        return "action_default_fallback"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Send a fallback message
        language = tracker.get_slot("language") or "en"
        
        if language == "vi":
            dispatcher.utter_message(text="Tôi xin lỗi, tôi không hiểu ý của bạn. Bạn có thể diễn đạt lại được không?")
        else:
            dispatcher.utter_message(text="I'm sorry, I didn't understand that. Could you rephrase?")
        
        # Revert the user utterance that triggered the fallback
        return [UserUtteranceReverted()]

class ActionDefaultAskAffirmation(Action):
    """Ask for affirmation when the bot is not confident."""

    def name(self) -> Text:
        return "action_default_ask_affirmation"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the predicted intent with low confidence
        intent = tracker.latest_message.get("intent", {}).get("name", "")
        
        language = tracker.get_slot("language") or "en"
        
        if language == "vi":
            dispatcher.utter_message(text=f"Tôi hiểu bạn đang muốn {intent}. Có đúng không?")
        else:
            dispatcher.utter_message(text=f"I understand you want to {intent}. Is that correct?")
        
        return []

class ActionDefaultAskRephrase(Action):
    """Ask the user to rephrase when the bot is not confident."""

    def name(self) -> Text:
        return "action_default_ask_rephrase"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        language = tracker.get_slot("language") or "en"
        
        if language == "vi":
            dispatcher.utter_message(text="Tôi không chắc tôi hiểu được. Bạn có thể diễn đạt theo cách khác được không?")
        else:
            dispatcher.utter_message(text="I'm not sure I understand. Can you rephrase that?")
        
        return []

class ActionRestart(Action):
    """Restart the conversation."""

    def name(self) -> Text:
        return "action_restart"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        language = tracker.get_slot("language") or "en"
        
        if language == "vi":
            dispatcher.utter_message(text="Đã bắt đầu lại cuộc trò chuyện.")
        else:
            dispatcher.utter_message(text="Restarting the conversation.")
        
        return []

class ActionBack(Action):
    """Go back to the previous conversation state."""

    def name(self) -> Text:
        return "action_back"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        language = tracker.get_slot("language") or "en"
        
        if language == "vi":
            dispatcher.utter_message(text="Quay lại bước trước.")
        else:
            dispatcher.utter_message(text="Going back to the previous step.")
        
        return []
