# Crypto Wallet Contacts Bot

A multilingual (Vietnamese/English) Rasa-based chatbot for managing cryptocurrency wallet contacts, using `rasa/LaBSE` model for improved multilingual understanding.

## Features

- Multilingual support (Vietnamese and English)
- Advanced NLU using `rasa/LaBSE` embeddings
- Custom Vietnamese tokenization using `underthesea`
- Claude integration as fallback for complex queries
- Cryptocurrency address validation
- Optimized for CPU-only environments

## System Requirements

- Python 3.8-3.10
- 8+ vCPU cores (recommended)
- 24GB+ RAM (recommended)
- 200GB+ storage

## Installation

### Step 1: Install Dependencies

```bash
# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Setup and Verify

Run the setup script to verify your environment and download required models:

```bash
python setup.py
```

This script will:
- Check Python version compatibility
- Verify all dependencies are installed
- Download and test the `rasa/LaBSE` model
- Verify `underthesea` functionality
- Test the custom tokenizer
- Create necessary directories
- Check hardware compatibility

### Step 3: Train the Model

```bash
rasa train
```

This will train the NLU model with the optimized pipeline in `config.yml`.

### Step 4: Start the Action Server

In a separate terminal:

```bash
# Set the Anthropic API key for Claude fallback (if using)
export ANTHROPIC_API_KEY=your_api_key_here

# Start the action server
rasa run actions
```

### Step 5: Start the Rasa Server

```bash
rasa run --enable-api
```

Or for testing in shell mode:

```bash
rasa shell
```

## Project Structure

- `config.yml`: Main Rasa configuration with `rasa/LaBSE` setup
- `custom/tokenizers.py`: Custom tokenizers for Vietnamese
- `actions/`: Custom actions including:
  - `actions.py`: Main actions for wallet management
  - `fallback_claude.py`: Claude integration for fallback handling
- `data/`: Training data (intents, stories, rules)
- `domain.yml`: Bot domain definition
- `setup.py`: Environment validation script

## Environment Variable Configuration

- `ANTHROPIC_API_KEY`: Required for Claude fallback integration

## Optimizing for Your Hardware

The default configuration is optimized for 24GB RAM and 8 vCPU. If you need to optimize further:

1. In `config.yml`, adjust these parameters:
   - Reduce `batch_size` to 8 or 4
   - Reduce `epochs` in `DIETClassifier` to 50
   - Set lower `evaluate_every_number_of_epochs` (e.g., 10)

2. Memory management:
   - Ensure the `cache_dir` is on an SSD for faster access
   - Consider using smaller training datasets for initial development

## Troubleshooting

### Out of Memory Errors

If you encounter OOM errors during training:

```bash
# Edit config.yml to reduce batch_size and epochs
# Then train with reduced memory usage
CUDA_VISIBLE_DEVICES= rasa train --augmentation 0
```

### Model Loading Issues

If the LaBSE model fails to load:

```bash
# Clear the cache and try again
rm -rf ./cache
python setup.py
```

### Vietnamese Tokenization Problems

If `underthesea` is not working correctly:

```bash
# Reinstall with specific version
pip uninstall underthesea -y
pip install underthesea==6.2.0
```

## Contributing

Contributions are welcome! Please check the issues page for tasks or create a pull request with improvements.

## License

[Your License Here]
