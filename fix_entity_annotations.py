#!/usr/bin/env python
"""
Script to check and fix misaligned entity annotations in Rasa NLU data.
This helps prevent the 'Misaligned entity annotation' warning during training.
"""

import os
import sys
import re
import yaml
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("entity_fixer")

def tokenize_simple(text: str) -> List[Tuple[int, int, str]]:
    """
    Simple tokenizer that returns tokens with their start and end positions.
    This is a simplified version that tries to match Rasa's tokenization.
    
    Args:
        text: The text to tokenize
        
    Returns:
        List of tuples of (start, end, token)
    """
    # Regex pattern to detect word boundaries
    # This is a simplified version and might not match Rasa's tokenization exactly
    pattern = r'\b\w+\b|\S'
    
    tokens = []
    for match in re.finditer(pattern, text):
        start, end = match.span()
        token = text[start:end]
        tokens.append((start, end, token))
    
    return tokens

def find_entity_annotation_issues(
    example: str, 
    entities: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Find issues with entity annotations by checking if they align with token boundaries.
    
    Args:
        example: The example text
        entities: List of entity dictionaries
        
    Returns:
        List of entity dictionaries with fixed boundaries
    """
    tokens = tokenize_simple(example)
    fixed_entities = []
    
    for entity in entities:
        entity_start = entity["start"]
        entity_end = entity["end"]
        entity_value = entity["value"]
        entity_type = entity["entity"]
        
        # Check if entity boundaries match token boundaries
        is_token_start = any(token[0] == entity_start for token in tokens)
        is_token_end = any(token[1] == entity_end for token in tokens)
        
        if not is_token_start or not is_token_end:
            logger.warning(f"Misaligned entity '{entity_value}' ({entity_type}) in example: '{example}'")
            logger.warning(f"Original boundaries: ({entity_start}, {entity_end})")
            
            # Find closest token boundaries
            best_start = entity_start
            best_end = entity_end
            
            # Find closest token start
            for token_start, token_end, token in tokens:
                if abs(token_start - entity_start) < abs(best_start - entity_start):
                    best_start = token_start
            
            # Find closest token end that is after the start
            for token_start, token_end, token in tokens:
                if token_end > best_start and abs(token_end - entity_end) < abs(best_end - entity_end):
                    best_end = token_end
            
            # Update entity with fixed boundaries
            fixed_entity = entity.copy()
            fixed_entity["start"] = best_start
            fixed_entity["end"] = best_end
            fixed_entity["value"] = example[best_start:best_end]
            
            logger.warning(f"Fixed boundaries: ({best_start}, {best_end})")
            logger.warning(f"Fixed value: '{fixed_entity['value']}'")
            
            fixed_entities.append(fixed_entity)
        else:
            fixed_entities.append(entity)
    
    return fixed_entities

def process_nlu_data(data_file: Path) -> Tuple[bool, Dict[str, Any]]:
    """
    Process NLU data file to fix entity annotations.
    
    Args:
        data_file: Path to NLU data file
        
    Returns:
        Tuple of (was_modified, modified_data)
    """
    with open(data_file, 'r', encoding='utf-8') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {data_file}: {e}")
            return False, {}
    
    if not data:
        logger.warning(f"No data found in {data_file}")
        return False, {}
    
    # Check if this is an NLU file
    if 'nlu' not in data:
        logger.info(f"No NLU data found in {data_file}, skipping")
        return False, data
    
    modified = False
    
    for i, item in enumerate(data['nlu']):
        if 'examples' not in item:
            continue
        
        examples_str = item['examples']
        if not examples_str:
            continue
        
        # Process each example that has entity annotations
        new_examples = []
        for line in examples_str.split('\n'):
            line = line.strip()
            if not line:
                new_examples.append(line)
                continue
            
            # Look for entity annotations like [entity](type)
            if '[' in line and '](' in line:
                # Extract entities
                entities = []
                remaining_text = line
                plain_text = ""
                
                while '[' in remaining_text and '](' in remaining_text:
                    # Get text before entity
                    before_entity = remaining_text.split('[', 1)[0]
                    plain_text += before_entity
                    
                    # Get entity part
                    entity_part = remaining_text.split('[', 1)[1]
                    if '](' not in entity_part:
                        break
                    
                    # Extract entity value and type
                    entity_value = entity_part.split('](', 1)[0]
                    entity_type_part = entity_part.split('](', 1)[1]
                    
                    if ')' not in entity_type_part:
                        break
                    
                    entity_type = entity_type_part.split(')', 1)[0]
                    
                    # Record entity with positions
                    start = len(plain_text)
                    end = start + len(entity_value)
                    entities.append({
                        "start": start,
                        "end": end,
                        "value": entity_value,
                        "entity": entity_type
                    })
                    
                    # Update plain text and remaining text
                    plain_text += entity_value
                    remaining_text = entity_type_part.split(')', 1)[1] if ')' in entity_type_part else ""
                
                # Add any remaining text
                plain_text += remaining_text
                
                # Fix entity annotations
                if entities:
                    fixed_entities = find_entity_annotation_issues(plain_text, entities)
                    
                    # Check if any entities were fixed
                    was_fixed = any(e1 != e2 for e1, e2 in zip(entities, fixed_entities))
                    
                    if was_fixed:
                        modified = True
                        # Rebuild the example with fixed entities
                        # We need to rebuild from the end to the beginning to avoid messing up the offsets
                        fixed_entities.sort(key=lambda e: e["start"], reverse=True)
                        fixed_line = plain_text
                        
                        for entity in fixed_entities:
                            # Insert entity annotation
                            fixed_line = (
                                fixed_line[:entity["start"]] + 
                                f"[{entity['value']}]({entity['entity']})" + 
                                fixed_line[entity["end"]:]
                            )
                        
                        line = fixed_line
                
                new_examples.append(line)
            else:
                new_examples.append(line)
        
        # Update examples
        data['nlu'][i]['examples'] = '\n'.join(new_examples)
    
    return modified, data

def fix_nlu_files(data_dir: Path) -> None:
    """
    Fix entity annotations in all NLU files in a directory.
    
    Args:
        data_dir: Directory containing NLU data files
    """
    # Find all YAML files in data directory and subdirectories
    yaml_files = list(data_dir.glob('**/*.yml'))
    yaml_files.extend(data_dir.glob('**/*.yaml'))
    
    fixed_count = 0
    
    for yaml_file in yaml_files:
        logger.info(f"Processing {yaml_file}...")
        modified, data = process_nlu_data(yaml_file)
        
        if modified:
            # Create backup
            backup_file = yaml_file.with_suffix(yaml_file.suffix + '.bak')
            logger.info(f"Creating backup at {backup_file}")
            
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")
                continue
            
            # Write fixed data
            try:
                with open(yaml_file, 'w', encoding='utf-8') as f:
                    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
                
                logger.info(f"Fixed entity annotations in {yaml_file}")
                fixed_count += 1
            except Exception as e:
                logger.error(f"Failed to write fixed data: {e}")
        else:
            logger.info(f"No issues found in {yaml_file}")
    
    if fixed_count > 0:
        logger.info(f"Fixed {fixed_count} files")
    else:
        logger.info("No files needed fixing")

def main():
    """Main function to run the entity fixer."""
    logger.info("Starting entity annotation fixer...")
    
    # Get the data directory
    data_dir = Path("./data")
    if not data_dir.exists():
        logger.error(f"Data directory {data_dir} does not exist")
        return 1
    
    # Fix NLU files
    fix_nlu_files(data_dir)
    
    logger.info("Entity annotation fixing completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
