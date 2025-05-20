#!/usr/bin/env python
"""
YAML Validator for Rasa files.
Validates the syntax of domain.yml, config.yml, and other YAML files.
"""

import sys
import os
import yaml
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("yaml_validator")

def validate_yaml_file(file_path):
    """Validate a single YAML file."""
    logger.info(f"Validating {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
            
        # Try to parse the YAML
        yaml_data = yaml.safe_load(yaml_content)
        
        # Additional checks for common Rasa file issues
        if file_path.endswith("domain.yml"):
            # Check for duplicate keys (YAML parser already catches this)
            # Check for required sections
            required_sections = ["intents", "responses", "actions", "entities", "slots"]
            missing_sections = [s for s in required_sections if s not in yaml_data]
            if missing_sections:
                logger.warning(f"Missing sections in domain.yml: {', '.join(missing_sections)}")
            
            # Check for actions referenced in responses but not defined
            utter_actions = [
                action for action in yaml_data.get("responses", {}).keys()
                if action.startswith("utter_")
            ]
            defined_actions = yaml_data.get("actions", [])
            missing_actions = [action for action in utter_actions if action not in defined_actions]
            if missing_actions:
                logger.warning(f"Actions referenced in responses but not defined in actions: {missing_actions}")
                
        elif file_path.endswith("config.yml"):
            # Check for required sections
            required_sections = ["pipeline", "policies"]
            missing_sections = [s for s in required_sections if s not in yaml_data]
            if missing_sections:
                logger.warning(f"Missing sections in config.yml: {', '.join(missing_sections)}")
        
        logger.info(f"✅ {file_path} is valid YAML")
        return True
    
    except yaml.YAMLError as e:
        logger.error(f"❌ Error in YAML file {file_path}:")
        logger.error(str(e))
        return False
    except Exception as e:
        logger.error(f"❌ Error validating file {file_path}:")
        logger.error(str(e))
        return False

def validate_all_yaml_files(directory="."):
    """Validate all YAML files in the directory."""
    yaml_files = list(Path(directory).glob("**/*.yml"))
    yaml_files.extend(Path(directory).glob("**/*.yaml"))
    
    valid_count = 0
    invalid_count = 0
    
    for file_path in yaml_files:
        valid = validate_yaml_file(file_path)
        if valid:
            valid_count += 1
        else:
            invalid_count += 1
    
    logger.info(f"==== Validation results ====")
    logger.info(f"Total YAML files checked: {valid_count + invalid_count}")
    logger.info(f"Valid YAML files: {valid_count}")
    logger.info(f"Invalid YAML files: {invalid_count}")
    
    return invalid_count == 0

def main():
    """Main function."""
    logger.info("Starting YAML validation...")
    
    if len(sys.argv) > 1:
        # Validate specific file
        file_path = sys.argv[1]
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return 1
            
        valid = validate_yaml_file(file_path)
        return 0 if valid else 1
    else:
        # Validate all YAML files in the current directory
        all_valid = validate_all_yaml_files()
        return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
