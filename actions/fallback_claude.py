from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted, FollowupAction
import anthropic
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionFallbackClaude(Action):
    """Custom fallback action that uses Claude API for responses."""

    def name(self) -> Text:
        return "action_fallback_claude"

    def run(self, 
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get the last user message
        user_message = tracker.latest_message.get("text", "")
        user_language = tracker.latest_message.get("language", "en")
        logger.info(f"Fallback to Claude for: '{user_message}' (language: {user_language})")
        
        # Try to get previous conversation context (last 5 turns)
        conversation_history = self._get_conversation_history(tracker, max_turns=5)
        
        try:
            # Use Claude API for response
            claude_response = self._get_claude_response(user_message, conversation_history, user_language)
            
            # Send Claude's response back to user
            dispatcher.utter_message(text=claude_response)
            
            logger.info(f"Claude fallback response: '{claude_response[:100]}...'")
            
            # Return events to revert the fallback action
            return [UserUtteranceReverted()]
            
        except Exception as e:
            logger.error(f"Error using Claude API: {str(e)}")
            
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
        
        # Convert to Claude's message format
        for event in events:
            role = "user" if event.get("event") == "user" else "assistant"
            text = event.get("text", "")
            if text:
                conversation.append({"role": role, "content": text})
                
        return conversation
            
    def _get_claude_response(self, 
                            user_message: str, 
                            conversation_history: List[Dict[str, str]], 
                            language: str) -> str:
        """Get a response from Claude API."""
        try:
            # Get API key from environment variable
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.error("ANTHROPIC_API_KEY environment variable not set")
                return self._get_fallback_message(language)
                
            # Initialize Claude client
            client = anthropic.Anthropic(api_key=api_key)
            
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
            messages = conversation_history.copy()
            
            # Add user's current message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from Claude
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                system=system_prompt,
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )
            
            # Extract response content
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error in Claude API call: {str(e)}")
            return self._get_fallback_message(language)
            
    def _get_fallback_message(self, language: str) -> str:
        """Return a fallback message if Claude API fails."""
        if language.lower() == "vi":
            return "Tôi xin lỗi, tôi không thể trả lời câu hỏi đó ngay bây giờ. Bạn có thể thử lại sau hoặc hỏi một câu hỏi khác."
        else:
            return "I'm sorry, I can't answer that question right now. Please try again later or ask a different question."
