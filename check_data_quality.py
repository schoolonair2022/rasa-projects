#!/usr/bin/env python
"""
Script to verify data quality and correct common issues in Rasa training data.
This helps prevent warnings and errors during training.
"""

import os
import sys
import yaml
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple, Optional
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("data_cleaner")

def count_intents_and_examples(data_files: List[Path]) -> Dict[str, int]:
    """
    Count the number of examples for each intent across all data files.
    
    Args:
        data_files: List of paths to NLU data files
        
    Returns:
        Dictionary mapping intent names to counts
    """
    intent_counts = {}
    
    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if not data or 'nlu' not in data:
                    continue
                
                for item in data['nlu']:
                    if 'intent' not in item:
                        continue
                    
                    intent = item['intent']
                    examples = item.get('examples', '')
                    if not examples:
                        continue
                    
                    # Count non-empty lines
                    example_count = len([line for line in examples.split('\n') if line.strip()])
                    
                    if intent in intent_counts:
                        intent_counts[intent] += example_count
                    else:
                        intent_counts[intent] = example_count
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    return intent_counts

def suggest_intents_to_merge(intent_counts: Dict[str, int], threshold: int = 5) -> List[List[str]]:
    """
    Suggest intents that might be candidates for merging based on low example count.
    
    Args:
        intent_counts: Dictionary mapping intent names to counts
        threshold: Minimum number of examples required
        
    Returns:
        List of groups of intents that might be merged
    """
    low_count_intents = {intent: count for intent, count in intent_counts.items() if count < threshold}
    
    # Simple way: just suggest merging intents with similar names
    similar_intents = {}
    for intent in low_count_intents:
        # Extract intent base name without language suffix
        base_name = re.sub(r'_(?:vi|en)$', '', intent)
        
        if base_name in similar_intents:
            similar_intents[base_name].append(intent)
        else:
            similar_intents[base_name] = [intent]
    
    # Return groups of similar intents with more than one intent
    return [group for group in similar_intents.values() if len(group) > 1]

def get_intent_examples(data_files: List[Path], intent: str) -> List[str]:
    """
    Get all examples for a specific intent from data files.
    
    Args:
        data_files: List of paths to NLU data files
        intent: Intent name to look for
        
    Returns:
        List of example strings
    """
    examples = []
    
    for file_path in data_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if not data or 'nlu' not in data:
                    continue
                
                for item in data['nlu']:
                    if item.get('intent') != intent:
                        continue
                    
                    example_text = item.get('examples', '')
                    if not example_text:
                        continue
                    
                    # Add non-empty lines
                    examples.extend([line.strip() for line in example_text.split('\n') if line.strip()])
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    return examples

def balance_intent_data(data_dir: Path, min_examples: int = 10) -> bool:
    """
    Analyze intent data and suggest how to balance it.
    
    Args:
        data_dir: Directory containing NLU data files
        min_examples: Minimum number of examples required per intent
        
    Returns:
        True if changes were made, False otherwise
    """
    # Find all YAML files in data directory and subdirectories
    yaml_files = list(data_dir.glob('**/*.yml'))
    yaml_files.extend(data_dir.glob('**/*.yaml'))
    
    # Count intent examples
    intent_counts = count_intents_and_examples(yaml_files)
    
    # Identify intents with too few examples
    low_count_intents = {intent: count for intent, count in intent_counts.items() if count < min_examples}
    
    if low_count_intents:
        logger.warning(f"Found {len(low_count_intents)} intents with fewer than {min_examples} examples:")
        for intent, count in low_count_intents.items():
            logger.warning(f"  - {intent}: {count} examples")
        
        # Suggest intents to merge
        suggestions = suggest_intents_to_merge(intent_counts, min_examples)
        
        if suggestions:
            logger.info("Consider merging these similar intents:")
            for group in suggestions:
                logger.info(f"  - {' + '.join(group)}")
        
        # Look at high-count intents for possible splitting
        high_count_intents = {intent: count for intent, count in intent_counts.items() if count > min_examples * 5}
        if high_count_intents:
            logger.info("These intents have many examples and might be candidates for splitting:")
            for intent, count in high_count_intents.items():
                logger.info(f"  - {intent}: {count} examples")
    else:
        logger.info(f"All intents have at least {min_examples} examples")
    
    return False  # No automatic changes made, just suggestions

def find_duplicate_examples(data_dir: Path) -> Dict[str, List[Tuple[str, str]]]:
    """
    Find duplicate examples across different intents.
    
    Args:
        data_dir: Directory containing NLU data files
        
    Returns:
        Dictionary mapping examples to list of (file, intent) tuples
    """
    # Find all YAML files in data directory and subdirectories
    yaml_files = list(data_dir.glob('**/*.yml'))
    yaml_files.extend(data_dir.glob('**/*.yaml'))
    
    # Track examples with their intents and files
    example_map = {}
    
    for file_path in yaml_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if not data or 'nlu' not in data:
                    continue
                
                for item in data['nlu']:
                    if 'intent' not in item:
                        continue
                    
                    intent = item['intent']
                    examples = item.get('examples', '')
                    if not examples:
                        continue
                    
                    for line in examples.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Strip entity annotations for comparison
                        # This is a simple approach that might not handle all edge cases
                        clean_example = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', line)
                        clean_example = clean_example.lower()
                        
                        if clean_example in example_map:
                            example_map[clean_example].append((str(file_path), intent))
                        else:
                            example_map[clean_example] = [(str(file_path), intent)]
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
    
    # Filter for duplicates
    duplicates = {example: locations for example, locations in example_map.items() if len(locations) > 1}
    
    return duplicates

def generate_data_quality_report(data_dir: Path) -> Dict[str, Any]:
    """
    Generate a comprehensive data quality report.
    
    Args:
        data_dir: Directory containing NLU data files
        
    Returns:
        Dictionary with report data
    """
    # Find all YAML files in data directory and subdirectories
    yaml_files = list(data_dir.glob('**/*.yml'))
    yaml_files.extend(data_dir.glob('**/*.yaml'))
    
    # Count intent examples
    intent_counts = count_intents_and_examples(yaml_files)
    
    # Find duplicates
    duplicates = find_duplicate_examples(data_dir)
    
    # Collect intent and entity statistics
    total_examples = sum(intent_counts.values())
    avg_examples = total_examples / len(intent_counts) if intent_counts else 0
    
    report = {
        "intent_statistics": {
            "total_intents": len(intent_counts),
            "total_examples": total_examples,
            "average_examples_per_intent": avg_examples,
            "intent_counts": intent_counts
        },
        "duplicate_examples": {
            "count": len(duplicates),
            "examples": [
                {
                    "text": example,
                    "locations": locations
                }
                for example, locations in duplicates.items()
            ] if len(duplicates) < 20 else []  # Only include if not too many
        }
    }
    
    return report

def print_data_quality_report(report: Dict[str, Any]) -> None:
    """
    Print a human-readable data quality report.
    
    Args:
        report: Dictionary with report data
    """
    intent_stats = report["intent_statistics"]
    
    logger.info("=== Data Quality Report ===")
    logger.info(f"Total intents: {intent_stats['total_intents']}")
    logger.info(f"Total examples: {intent_stats['total_examples']}")
    logger.info(f"Average examples per intent: {intent_stats['average_examples_per_intent']:.1f}")
    
    # Print intents with very few examples
    low_count_threshold = 5
    low_count_intents = {i: c for i, c in intent_stats['intent_counts'].items() if c < low_count_threshold}
    if low_count_intents:
        logger.warning(f"\nIntents with fewer than {low_count_threshold} examples:")
        for intent, count in sorted(low_count_intents.items(), key=lambda x: x[1]):
            logger.warning(f"  - {intent}: {count} examples")
    
    # Print duplicate examples
    duplicates = report["duplicate_examples"]
    if duplicates["count"] > 0:
        logger.warning(f"\nFound {duplicates['count']} duplicate examples across different intents")
        if duplicates["examples"]:
            logger.warning("Examples:")
            for i, dup in enumerate(duplicates["examples"][:5], 1):  # Show at most 5
                logger.warning(f"  {i}. '{dup['text']}'")
                for file_path, intent in dup["locations"]:
                    logger.warning(f"     - {intent} (in {os.path.basename(file_path)})")
            
            if duplicates["count"] > 5:
                logger.warning(f"  ... and {duplicates['count'] - 5} more")

def estimate_test_set_size_needed(intent_counts: Dict[str, int]) -> int:
    """
    Estimate the minimum test set size needed based on the number of intents.
    
    Args:
        intent_counts: Dictionary mapping intent names to counts
        
    Returns:
        Recommended test set size
    """
    return max(30, len(intent_counts))

def main():
    """Main function to run the data cleaner."""
    logger.info("Starting data quality analysis...")
    
    # Get the data directory
    data_dir = Path("./data")
    if not data_dir.exists():
        logger.error(f"Data directory {data_dir} does not exist")
        return 1
    
    # Generate and print report
    report = generate_data_quality_report(data_dir)
    print_data_quality_report(report)
    
    # Balance intent data
    balance_intent_data(data_dir)
    
    # Estimate test set size needed
    intent_counts = report["intent_statistics"]["intent_counts"]
    min_test_size = estimate_test_set_size_needed(intent_counts)
    logger.info(f"\nBased on your data, you need at least {min_test_size} examples for validation/testing")
    logger.info(f"Recommended config.yml setting: evaluate_on_number_of_examples: {min_test_size}")
    
    # Save report for future reference
    try:
        with open("data_quality_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        logger.info("Saved report to data_quality_report.json")
    except Exception as e:
        logger.error(f"Failed to save report: {e}")
    
    logger.info("Data quality analysis completed")
    return 0

if __name__ == "__main__":
    sys.exit(main())
