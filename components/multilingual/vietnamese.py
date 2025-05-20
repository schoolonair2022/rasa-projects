"""
Vietnamese text processing and tokenization for Rasa.
"""

import typing
import re
from typing import Any, List, Text, Dict, Optional

from rasa.engine.graph import ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message

from underthesea import word_tokenize as underthesea_tokenize

def process_vietnamese(text: Text) -> List[Text]:
    """Process Vietnamese text and return tokenized words."""
    return underthesea_tokenize(text)

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class UnderthesaTokenizer(Tokenizer):
    """Tokenizer using underthesea for Vietnamese language."""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "UnderthesaTokenizer":
        return cls(config)

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Initialize tokenizer with configuration."""
        super().__init__(component_config)
        self.component_config = component_config or {}
        self.intent_tokenization_flag = self.component_config.get("intent_tokenization_flag", False)
        self.intent_split_symbol = self.component_config.get("intent_split_symbol", "_")

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        """Tokenize the text using underthesea Vietnamese tokenizer."""
        text = message.get(attribute)
        
        if not text:
            return []

        # Detect language - if message has language attribute set to "vi", use underthesea
        # Otherwise default to WhitespaceTokenizer-like behavior
        language = message.get("language", "")
        if language == "vi":
            words = underthesea_tokenize(text)
        else:
            words = text.split()
        
        # Convert to Rasa Token objects
        running_offset = 0
        tokens = []
        
        for word in words:
            word_offset = text.find(word, running_offset)
            if word_offset != -1:
                token = Token(
                    text=word,
                    start=word_offset,
                    end=word_offset + len(word),
                )
                tokens.append(token)
                running_offset = word_offset + len(word)
                
        return tokens

    def process_tokens(self, tokens: List[Token], message: Message):
        """Process tokens after tokenization."""
        # Skip this part if not tokenizing intents
        if not self.intent_tokenization_flag:
            return tokens

        # If intent tokenization enabled, process intent classes
        for attribute in ["intent", "response"]:
            intent = message.get(attribute)
            if not intent:
                continue

            if isinstance(intent, str):
                # Split intent by the split symbol
                sub_intents = intent.split(self.intent_split_symbol)
                message.set(
                    attribute, 
                    sub_intents[0], 
                    add_to_output=True
                )
            
        return tokens
