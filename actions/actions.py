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
from . import crypto_utils

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
        
        logger.info("Resetting contact-related slots")
        # Ask if user wants to do something else
        dispatcher.utter_message(text="Is there anything else I can help you with?")
        return [SlotSet("contact_name", None), 
                SlotSet("wallet_address", None), 
                SlotSet("network_type", None),
                SlotSet("address_valid", None)]

# New actions using CryptoBERT

class ActionAnalyzeSentiment(Action):
    def name(self) -> Text:
        return "action_analyze_sentiment"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last user message
        message = tracker.latest_message.get('text')
        logger.info(f"Analyzing sentiment for: {message}")
        
        sentiment, confidence = crypto_utils.analyze_crypto_sentiment(message)
        logger.info(f"Sentiment analysis result: {sentiment}, confidence: {confidence}")
        
        if sentiment == "positive":
            dispatcher.utter_message(text=f"I notice you have a positive outlook on this topic! 📈")
        elif sentiment == "negative":
            dispatcher.utter_message(text=f"It seems you're concerned about this. Is there anything I can help with? 📉")
        else:
            dispatcher.utter_message(text=f"Thank you for sharing your perspective.")
        
        return [SlotSet("sentiment", sentiment),
                SlotSet("sentiment_confidence", confidence)]

class ActionDetectScam(Action):
    def name(self) -> Text:
        return "action_detect_scam"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get crypto description from slot
        description = tracker.get_slot("crypto_description")
        if not description:
            dispatcher.utter_message(text="Can you describe that project/token?")
            return []
        
        logger.info(f"Analyzing potential scam: {description}")
        is_scam, probability, indicators = crypto_utils.detect_crypto_scam(description)
        logger.info(f"Scam detection result: {is_scam}, probability: {probability}, indicators: {indicators}")
        
        if is_scam:
            dispatcher.utter_message(text="⚠️ Warning! This project has some suspicious signs:")
            if indicators:
                dispatcher.utter_message(text="- " + "\n- ".join(indicators))
            dispatcher.utter_message(text="Be careful and always do thorough research before investing.")
        else:
            dispatcher.utter_message(text="I don't detect clear signs of fraud, but you should still do your own research.")
        
        return [SlotSet("scam_probability", probability)]

class ActionClassifyTopic(Action):
    def name(self) -> Text:
        return "action_classify_topic"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last user message
        message = tracker.latest_message.get('text')
        logger.info(f"Classifying topic for: {message}")
        
        topic, confidence = crypto_utils.classify_crypto_topic(message)
        logger.info(f"Topic classification result: {topic}, confidence: {confidence}")
        
        # Route based on topic
        if topic == "investment":
            dispatcher.utter_message(text="I see you're talking about cryptocurrency investment. How can I help?")
        elif topic == "technical":
            dispatcher.utter_message(text="This is a technical question about blockchain. I'll try to explain clearly.")
        elif topic == "security":
            dispatcher.utter_message(text="Security is a crucial issue in cryptocurrency. Make sure you always take precautions.")
        else:
            dispatcher.utter_message(text="I can help you with many cryptocurrency topics. Which aspect are you interested in?")
        
        return [SlotSet("query_topic", topic)]

class ActionUpdateUserExpertise(Action):
    def name(self) -> Text:
        return "action_update_user_expertise"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last user message
        message = tracker.latest_message.get('text')
        logger.info(f"Determining expertise level for: {message}")
        
        expertise, confidence = crypto_utils.determine_expertise_level(message)
        logger.info(f"Expertise level result: {expertise}, confidence: {confidence}")
        
        # Customize response based on expertise
        if expertise == "beginner":
            dispatcher.utter_message(text="I'll simplify my explanations to help you understand better.")
        elif expertise == "expert":
            dispatcher.utter_message(text="I see you have a deep understanding of cryptocurrencies. I'll provide more in-depth details.")
        else:
            dispatcher.utter_message(text="I'll provide information balanced between basic and advanced concepts.")
        
        return [SlotSet("expertise_level", expertise)]

class ActionExtractCryptoEntities(Action):
    def name(self) -> Text:
        return "action_extract_crypto_entities"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last user message
        message = tracker.latest_message.get('text')
        logger.info(f"Extracting crypto entities from: {message}")
        
        entities = crypto_utils.extract_crypto_entities(message)
        logger.info(f"Extracted entities: {entities}")
        
        # Respond based on extracted entities
        if entities['tokens']:
            token_list = ", ".join(entities['tokens'])
            dispatcher.utter_message(text=f"I see you're talking about these tokens: {token_list}")
        
        if entities['blockchains']:
            blockchain_list = ", ".join(entities['blockchains'])
            dispatcher.utter_message(text=f"Blockchains mentioned: {blockchain_list}")
        
        if not entities['tokens'] and not entities['blockchains']:
            dispatcher.utter_message(text="I couldn't detect specific tokens or blockchains in your message.")
        
        # Save to slots
        return [SlotSet("mentioned_tokens", entities['tokens']),
                SlotSet("mentioned_blockchains", entities['blockchains'])]

# Add a new action to handle fallback and context switching
class ActionHandleContextSwitch(Action):
    def name(self) -> Text:
        return "action_handle_context_switch"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the active intent
        latest_intent = tracker.latest_message.get('intent', {}).get('name')
        logger.info(f"Handling context switch from intent: {latest_intent}")
        
        # Check if we were in the middle of a contact flow
        contact_name = tracker.get_slot("contact_name")
        wallet_address = tracker.get_slot("wallet_address")
        
        if contact_name and not wallet_address:
            # We were in the middle of adding a contact but switched context
            dispatcher.utter_message(text="I notice we were adding a contact. Would you like to continue with that or focus on your new question?")
        
        # Clear slots that might be context-dependent
        return [SlotSet("active_context", latest_intent)]
    

class ActionAskCryptoClarification(Action):
    def name(self) -> Text:
        return "action_ask_crypto_clarification"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # Lấy tin nhắn gần nhất của người dùng
        user_message = tracker.latest_message.get("text", "").lower()
        
        # Trích xuất các viết tắt tiềm năng 
        # Ví dụ, tìm tất cả các từ 2-5 ký tự không phải là từ phổ biến
        words = re.findall(r'\b[a-z]{2,5}\b', user_message)
        crypto_related_words = [word for word in words if word not in ['with', 'and', 'the', 'to', 'for', 'of', 'his', 'her']]
        
        if crypto_related_words:
            abbreviation = crypto_related_words[0]  # Lấy ứng viên đầu tiên
            message = f"Could you specify which cryptocurrency you mean by '{abbreviation}'? There are several possibilities."
        else:
            message = "Could you specify which cryptocurrency you're referring to? There are several possibilities."
        
        dispatcher.utter_message(text=message)
        return []