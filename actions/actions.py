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
            dispatcher.utter_message(text=f"Tôi nhận thấy bạn có quan điểm tích cực về chủ đề này! 📈")
        elif sentiment == "negative":
            dispatcher.utter_message(text=f"Có vẻ bạn đang lo lắng về điều này. Tôi có thể giúp gì không? 📉")
        else:
            dispatcher.utter_message(text=f"Cảm ơn bạn đã chia sẻ quan điểm của mình.")
        
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
            dispatcher.utter_message(text="Bạn có thể mô tả dự án/token đó không?")
            return []
        
        logger.info(f"Analyzing potential scam: {description}")
        is_scam, probability, indicators = crypto_utils.detect_crypto_scam(description)
        logger.info(f"Scam detection result: {is_scam}, probability: {probability}, indicators: {indicators}")
        
        if is_scam:
            dispatcher.utter_message(text="⚠️ Cảnh báo! Dự án này có một số dấu hiệu đáng ngờ:")
            if indicators:
                dispatcher.utter_message(text="- " + "\n- ".join(indicators))
            dispatcher.utter_message(text="Hãy cẩn thận và luôn nghiên cứu kỹ trước khi đầu tư.")
        else:
            dispatcher.utter_message(text="Tôi không phát hiện các dấu hiệu lừa đảo rõ ràng, nhưng vẫn nên nghiên cứu thêm.")
        
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
            dispatcher.utter_message(text="Tôi thấy bạn đang nói về đầu tư tiền điện tử. Tôi có thể giúp gì không?")
        elif topic == "technical":
            dispatcher.utter_message(text="Đây là một câu hỏi kỹ thuật về blockchain. Tôi sẽ cố gắng giải thích rõ ràng.")
        elif topic == "security":
            dispatcher.utter_message(text="Bảo mật là vấn đề rất quan trọng trong tiền điện tử. Hãy đảm bảo bạn luôn thực hiện các biện pháp phòng ngừa.")
        else:
            dispatcher.utter_message(text="Tôi có thể giúp bạn với nhiều chủ đề về tiền điện tử. Bạn quan tâm đến khía cạnh nào?")
        
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
            dispatcher.utter_message(text="Tôi sẽ đơn giản hóa các giải thích của mình để giúp bạn hiểu rõ hơn.")
        elif expertise == "expert":
            dispatcher.utter_message(text="Tôi thấy bạn đã có hiểu biết sâu sắc về tiền điện tử. Tôi sẽ cung cấp các chi tiết chuyên sâu hơn.")
        else:
            dispatcher.utter_message(text="Tôi sẽ cung cấp thông tin cân bằng giữa cơ bản và chuyên sâu.")
        
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
            dispatcher.utter_message(text=f"Tôi thấy bạn đang nói về các token: {token_list}")
        
        if entities['blockchains']:
            blockchain_list = ", ".join(entities['blockchains'])
            dispatcher.utter_message(text=f"Blockchain được đề cập: {blockchain_list}")
        
        if not entities['tokens'] and not entities['blockchains']:
            dispatcher.utter_message(text="Tôi không phát hiện được token hoặc blockchain cụ thể trong tin nhắn của bạn.")
        
        # Save to slots
        return [SlotSet("mentioned_tokens", entities['tokens']),
                SlotSet("mentioned_blockchains", entities['blockchains'])]