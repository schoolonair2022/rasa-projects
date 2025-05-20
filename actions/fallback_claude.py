from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, FollowupAction
import os
import logging
import openai  # Thay thế anthropic bằng openai

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionFallbackClaude(Action):
    """Custom fallback action that uses OpenAI API for responses."""

    def name(self) -> Text:
        return "action_fallback_claude"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last user message
        user_message = tracker.latest_message.get("text", "")
        user_language = tracker.latest_message.get("language", "en")
        logger.info(f"Fallback to OpenAI for: '{user_message}' (language: {user_language})")
        
        # Try to get previous conversation context (last 5 turns)
        conversation_history = self._get_conversation_history(tracker, max_turns=5)
        
        try:
            # Use OpenAI API for response
            openai_response = self._get_openai_response(user_message, conversation_history, user_language)
            
            # Send OpenAI's response back to user
            dispatcher.utter_message(text=openai_response)
            
            logger.info(f"OpenAI fallback response: '{openai_response[:100]}...'")
            
            # Return events to revert the fallback action
            return [UserUtteranceReverted()]
            
        except Exception as e:
            logger.error(f"Error using OpenAI API: {str(e)}")
            
            # Fallback message in the appropriate language
            if user_language.lower() == "vi":
                fallback_msg = "Tôi không hiểu rõ yêu cầu của bạn. Bạn có thể giải thích rõ hơn được không?"
            else:
                fallback_msg = "I'm not sure I understand. Could you please rephrase that?"
                
            dispatcher.utter_message(text=fallback_msg)
            return [UserUtteranceReverted()]
            
    def _get_conversation_history(self, tracker: Tracker, max_turns: int = 5) -> List[Dict[str, str]]:
        """Extract recent conversation history."""
        conversation = []
        
        # Get the events that are either user or bot messages, reverse to get newest first
        events = [e for e in tracker.events if e.get("event") in ["user", "bot"]]
        events.reverse()
        
        # Get at most max_turns * 2 events (user + bot for each turn)
        events = events[:max_turns * 2]
        events.reverse()  # Reverse back to chronological order
        
        # Convert to a format suitable for OpenAI
        for event in events:
            role = "user" if event.get("event") == "user" else "assistant"
            text = event.get("text", "")
            if text:
                conversation.append({"role": role, "content": text})
                
        return conversation
            
    def _get_openai_response(self, 
                            user_message: str, 
                            conversation_history: List[Dict[str, str]], 
                            language: str) -> str:
        """Get a response from OpenAI API."""
        try:
            # Get API key from environment variable
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.error("OPENAI_API_KEY environment variable not set")
                return self._get_fallback_message(language)
                
            # Set the API key
            openai.api_key = api_key
            
            # Create system prompt based on language
            if language.lower() == "vi":
                system_prompt = """
                Bạn là trợ lý ảo trò chuyện của một ví tiền điện tử. Hãy trả lời các câu hỏi một cách ngắn gọn và hữu ích.
                Ngôn ngữ chính của bạn là tiếng Việt. Nếu người dùng hỏi về ví tiền điện tử, địa chỉ ví, chuyển tiền, hoặc
                các chức năng quản lý ví, hãy khuyên họ sử dụng các tính năng có sẵn trong ứng dụng ví.
                """
            else:
                system_prompt = """
                You are a conversational assistant for a cryptocurrency wallet app. Answer questions concisely and helpfully.
                Your primary language is English. If users ask about wallet functionality, wallet addresses, transfers, or
                wallet management, advise them to use the built-in features of the wallet app.
                """
                
            # Create messages from history and current message
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            
            # Add user's current message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Sử dụng gpt-3.5-turbo thay vì Claude
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            # Extract response content
            return response.choices[0].message["content"]
            
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            return self._get_fallback_message(language)
            
    def _get_fallback_message(self, language: str) -> str:
        """Return a fallback message if OpenAI API fails."""
        if language.lower() == "vi":
            return "Tôi xin lỗi, tôi không thể trả lời câu hỏi đó ngay bây giờ. Bạn có thể thử lại sau hoặc hỏi một câu hỏi khác."
        else:
            return "I'm sorry, I can't answer that question right now. Please try again later or ask a different question."
