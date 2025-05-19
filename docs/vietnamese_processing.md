# Vietnamese Text Processing Guide

This document provides guidance for handling Vietnamese text in your Rasa chatbot using the `rasa/LaBSE` model and `underthesea` tokenization.

## Vietnamese Language Characteristics

Vietnamese has some unique characteristics that affect NLP:

1. **Tonal language**: Vietnamese uses diacritics for tone marks (e.g., á, à, ả, ã, ạ)
2. **Word compounds**: Many Vietnamese concepts are expressed with compound words
3. **No spaces between syllables** in compound words, making tokenization challenging
4. **Different dialects**: Northern, Central, and Southern dialects have differences
5. **Code-switching**: Vietnamese speakers often mix Vietnamese with English

## Tokenization with `underthesea`

Our chatbot uses `underthesea` for Vietnamese tokenization. This library:

- Properly segments Vietnamese compound words
- Handles Vietnamese diacritics correctly
- Provides better tokenization than basic whitespace tokenizers

Example:
```python
from underthesea import word_tokenize

# Input text
text = "Tôi muốn thêm địa chỉ ví Bitcoin của tôi vào danh bạ"

# Tokenization
tokens = word_tokenize(text)
print(tokens)
# Output: ['Tôi', 'muốn', 'thêm', 'địa_chỉ', 'ví', 'Bitcoin', 'của', 'tôi', 'vào', 'danh_bạ']
```

Notice how "địa_chỉ" (address) and "danh_bạ" (contacts) are tokenized as single units.

## Training Data Considerations

When preparing training data:

1. **Include Vietnamese-specific examples**: 
   - Add examples with Vietnamese diacritics
   - Include examples without diacritics (users sometimes omit them)
   - Add regional variations of common phrases

2. **Handle mixed language utterances**:
   - Include examples where users mix Vietnamese and English
   - Add examples with cryptocurrency terms that aren't translated

3. **Entity annotation**:
   - Be consistent in entity annotation across languages
   - Check that entity spans properly follow Vietnamese word boundaries

Example:
```yaml
- intent: add_contact_vi
  examples: |
    - Thêm [Nguyen Van A](contact_name) vào danh bạ của tôi
    - Lưu địa chỉ [0x123abc](wallet_address) cho [Mai](contact_name)
    - Thêm [John](contact_name) với address [0xabc123](wallet_address)  # Mixed language
```

## Language Detection Approach

Our approach uses `rasa/LaBSE` embeddings to detect the language:

1. For messages in Vietnamese, we use the Vietnamese tokenizer
2. For messages in English, we use the whitespace tokenizer
3. For mixed language, we handle with a special tokenization strategy

The `MultilingualTokenizer` automatically routes to the appropriate language-specific tokenizer.

## Testing Vietnamese Support

To test Vietnamese support:

1. Use the provided `test_multilingual.py` script
2. Try mixed language inputs to check language detection
3. Test with and without diacritics
4. Verify entity extraction works for Vietnamese phrases

## Common Issues

1. **Diacritics inconsistency**: 
   - Solution: Include training examples both with and without diacritics

2. **Entity extraction failures**: 
   - Solution: Check entity boundaries match Vietnamese word compounds

3. **Mixed language confusion**: 
   - Solution: Add more mixed language examples to training data

4. **Dialect variations**: 
   - Solution: Include examples covering Northern, Central, and Southern dialects

## Fallback Strategy

If Vietnamese NLU fails:

1. The system uses `FallbackClassifier` with a 0.7 threshold
2. The `action_fallback_claude` action is triggered
3. Claude handles the Vietnamese input using its multilingual capabilities

## Improving Vietnamese Performance

1. **Add more training data**: The more Vietnamese examples, the better
2. **Use real conversations**: Add examples from real user conversations
3. **Fine-tune thresholds**: Adjust confidence thresholds based on performance
4. **Regular updates**: Periodically retrain with new Vietnamese examples
