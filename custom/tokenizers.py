import typing
from typing import Any, List, Text, Dict, Optional

from rasa.engine.graph import ExecutionContext
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.tokenizers.tokenizer import Token, Tokenizer
from rasa.shared.nlu.training_data.message import Message

from underthesea import word_tokenize as underthesea_tokenize

@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class UnderthesaTokenizer(Tokenizer):
    """Custom tokenizer using underthesea for Vietnamese language."""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "UnderthesaTokenizer":
        return cls(config)

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        """Tokenize the text using underthesea Vietnamese tokenizer."""
        text = message.get(attribute)
        
        if not text:
            return []

        words = underthesea_tokenize(text)
        
        # Convert underthesea output to Rasa Token objects
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

# MultilingualTokenizer to handle both English and Vietnamese
@DefaultV1Recipe.register(
    [DefaultV1Recipe.ComponentType.MESSAGE_TOKENIZER], is_trainable=False
)
class MultilingualTokenizer(Tokenizer):
    """Multilingual tokenizer that dispatches to language-specific tokenizers."""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> "MultilingualTokenizer":
        return cls(config)

    def __init__(self, config: Dict[Text, Any]) -> None:
        """Initialize the tokenizer with language-specific interfaces."""
        super().__init__(config)
        self.language_interfaces = {}
        
        # Create language-specific tokenizers based on config
        language_interfaces = config.get("languageInterfaces", {})
        
        for lang, tokenizer_config in language_interfaces.items():
            tokenizer_name = tokenizer_config.get("name")
            if tokenizer_name == "UnderthesaTokenizer":
                from custom.tokenizers import UnderthesaTokenizer
                self.language_interfaces[lang] = UnderthesaTokenizer(tokenizer_config)
            elif tokenizer_name == "WhitespaceTokenizer":
                from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
                self.language_interfaces[lang] = WhitespaceTokenizer(tokenizer_config)
                
        # Default to WhitespaceTokenizer if no match
        from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
        self.default_tokenizer = WhitespaceTokenizer({})
        
        # Copy other config settings
        self.intent_tokenization_flag = config.get("intent_tokenization_flag", False)
        self.intent_split_symbol = config.get("intent_split_symbol", "_")

    def tokenize(self, message: Message, attribute: Text) -> List[Token]:
        """Dispatch to the appropriate language tokenizer based on message language."""
        # Get language from message metadata or default to English
        language = message.get("language", "en")
        
        # Use the appropriate tokenizer
        if language in self.language_interfaces:
            tokenizer = self.language_interfaces[language]
            return tokenizer.tokenize(message, attribute)
        else:
            # Fall back to default tokenizer
            return self.default_tokenizer.tokenize(message, attribute)
