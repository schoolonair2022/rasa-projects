#!/usr/bin/env python
"""
Fix script for Rasa MemoizationPolicy error.
This script creates/fixes model files to resolve the
'AttributeError: 'dict' object has no attribute 'prediction_states'' error.
"""

import os
import sys
import shutil
import logging
import json
import subprocess
from pathlib import Path
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("policy_fixer")

def find_latest_model():
    """Find the most recent model directory."""
    models_dir = Path("./models")
    if not models_dir.exists():
        logger.error("Models directory not found. Please train a model first.")
        return None
        
    # List all model files
    model_files = list(models_dir.glob("*.tar.gz"))
    if not model_files:
        logger.error("No model files found in the models directory.")
        return None
        
    # Sort by modification time (newest first)
    latest_model = max(model_files, key=lambda p: p.stat().st_mtime)
    logger.info(f"Found latest model: {latest_model}")
    return latest_model

def extract_model(model_path):
    """Extract model archive to a temporary directory."""
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Extracting model to temporary directory: {temp_dir}")
    
    try:
        subprocess.run(
            ["tar", "-xzf", str(model_path), "-C", temp_dir],
            check=True,
            capture_output=True
        )
        return temp_dir
    except subprocess.CalledProcessError as e:
        logger.error(f"Error extracting model: {e}")
        logger.error(f"stdout: {e.stdout.decode()}")
        logger.error(f"stderr: {e.stderr.decode()}")
        shutil.rmtree(temp_dir)
        return None

def fix_policy_featurizers(model_dir):
    """Fix featurizer configuration for all policies in the model."""
    # Check for core policy file
    core_policy_path = os.path.join(model_dir, "core", "policy_metadata.json")
    if not os.path.exists(core_policy_path):
        logger.error(f"Policy metadata file not found: {core_policy_path}")
        return False
    
    # Read policy metadata
    with open(core_policy_path, 'r') as f:
        metadata = json.load(f)
    
    # Get policy names
    policies = metadata.get("policy_names", [])
    fixed_policies = []
    
    # Fix each policy with featurizer issues
    policy_dict = metadata.get("policy_priority", {})
    
    for i, policy_name in enumerate(policies):
        if policy_name in ["MemoizationPolicy", "RulePolicy", "TEDPolicy"]:
            if str(i) in policy_dict:
                logger.info(f"Checking {policy_name} configuration...")
                featurizer_info = policy_dict.get(str(i), {}).get("featurizer", {})
                
                if isinstance(featurizer_info, dict) and "name" not in featurizer_info:
                    logger.info(f"Fixing {policy_name} featurizer configuration...")
                    
                    # Fix the featurizer configuration
                    policy_dict[str(i)]["featurizer"] = {
                        "name": "MaxHistoryTrackerFeaturizer",
                        "max_history": 5,
                        "state_featurizer": {
                            "name": "SingleStateFeaturizer"
                        }
                    }
                    fixed_policies.append(policy_name)
    
    if fixed_policies:
        # Update the metadata
        metadata["policy_priority"] = policy_dict
        
        # Write the updated metadata back to the file
        with open(core_policy_path, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        logger.info(f"Fixed featurizer configuration for policies: {', '.join(fixed_policies)}")
        return True
    else:
        logger.info("No policy featurizers needed fixing.")
        return True

def repackage_model(model_dir, original_model_path):
    """Package the fixed model back into a .tar.gz file."""
    output_model_path = str(original_model_path).replace(".tar.gz", "_fixed.tar.gz")
    logger.info(f"Repackaging model to: {output_model_path}")
    
    try:
        # Create tar.gz archive
        current_dir = os.getcwd()
        os.chdir(model_dir)
        
        subprocess.run(
            ["tar", "-czf", output_model_path, "."],
            check=True,
            capture_output=True
        )
        
        os.chdir(current_dir)
        logger.info(f"Model repackaged successfully: {output_model_path}")
        return output_model_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Error repackaging model: {e}")
        logger.error(f"stdout: {e.stdout.decode()}")
        logger.error(f"stderr: {e.stderr.decode()}")
        return None

def main():
    """Main function to fix MemoizationPolicy error."""
    logger.info("Starting Policy Featurizer fixer...")
    
    # Find the latest model
    model_path = find_latest_model()
    if not model_path:
        return 1
    
    # Extract the model
    temp_dir = extract_model(model_path)
    if not temp_dir:
        return 1
    
    try:
        # Fix Policy Featurizers
        if fix_policy_featurizers(temp_dir):
            # Repackage the model
            fixed_model_path = repackage_model(temp_dir, model_path)
            if fixed_model_path:
                logger.info("=== 🎉 Model fixed successfully! ===")
                logger.info(f"You can now use the fixed model with: rasa shell --model {fixed_model_path}")
            else:
                logger.error("Failed to repackage the model.")
                return 1
        else:
            logger.error("Failed to fix policy featurizers.")
            return 1
    finally:
        # Clean up
        logger.info(f"Cleaning up temporary directory: {temp_dir}")
        shutil.rmtree(temp_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
