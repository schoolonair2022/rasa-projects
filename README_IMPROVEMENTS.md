# Rasa Crypto Wallet Contact Management Improvements

This branch contains significant improvements to the cryptocurrency wallet contact management functionality, focusing on enhancing the multilingual support, entity recognition, and validation processes.

## Key Improvements

### 1. Vietnamese Language Support
- Integrated `underthesea` tokenizer to properly handle Vietnamese text tokenization
- Added Vietnamese responses for all contact-related interactions
- Enhanced the multilingual capabilities of the entity extraction pipeline

### 2. Enhanced Cryptocurrency Network Handling
- Expanded the list of supported cryptocurrency networks
- Added comprehensive synonyms and lookup tables for crypto networks
- Implemented typo detection and correction for network names
- Added proper handling of common abbreviations (BTC, ETH, SOL, etc.)

### 3. Improved Wallet Address Validation
- Enhanced wallet address validation for multiple cryptocurrency formats
- Added regex patterns for various wallet address formats
- Implemented network-address mismatch detection to provide better feedback
- Improved validation messages in both English and Vietnamese

### 4. Better Form Handling
- Restructured the form slot mapping for better entity handling
- Added more comprehensive form validation
- Improved error handling and user guidance during the form filling process

### 5. Testing Improvements
- Added comprehensive test files for both English and Vietnamese scenarios
- Created test cases for typo handling and error recovery
- Implemented a test script to evaluate NLU performance

### 6. Configuration Optimizations
- Increased training epochs for better model performance
- Updated the pipeline configuration for better entity recognition
- Optimized parameters based on available hardware (8 vCPU, 24 GB RAM)

## Technical Details

### Pipeline Enhancements
1. Added `underthesea` tokenizer for Vietnamese
2. Increased epochs in `LanguageModelFeaturizer` from 5 to 15
3. Optimized `DIETClassifier` with `batch_strategy: "sequence"` 
4. Added validation split for performance monitoring
5. Improved the ranking logic for more focused intent detection

### New Dependencies
- Configured use of the existing `underthesea` dependency for Vietnamese NLP

### Testing
A test script is provided at `test_improved_contact.py` which can be used to evaluate the NLU performance on various test cases.

## Usage

To train a model with the improved configuration:
```bash
rasa train
```

To test the improvements:
```bash
python test_improved_contact.py
```

To run the interactive tests:
```bash
rasa interactive
```

## Key Files
- `config.yml`: Updated with enhanced pipeline configuration
- `domain.yml`: Added proper slot mappings and improved response templates
- `data/contact/crypto_lookup.yml`: New file with lookup tables for cryptos
- `actions/contact/action_validate_wallet_address.py`: Enhanced address validation
- `actions/contact/action_validate_crypto_network.py`: Improved network validation
- `tests/contact/test_improved_*.yml`: New test cases for verification

## Next Steps
1. Consider adding additional language support beyond Vietnamese
2. Expand the cryptocurrency network list as new popular networks emerge
3. Implement additional feedback mechanisms for validation failures
4. Consider adding memory/cache for previously seen wallet addresses