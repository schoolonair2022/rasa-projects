import yaml
import sys
import os

def validate_yaml_file(file_path):
    try:
        with open(file_path, 'r') as f:
            yaml.safe_load(f)
        print(f"✅ {file_path} is valid YAML")
        return True
    except yaml.YAMLError as e:
        print(f"❌ {file_path} has YAML errors:")
        print(e)
        return False

def validate_all_yaml_files(directory):
    all_valid = True
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.yml'):
                file_path = os.path.join(root, file)
                if not validate_yaml_file(file_path):
                    all_valid = False
    return all_valid

if __name__ == "__main__":
    directory = "."
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    
    if validate_all_yaml_files(directory):
        print("\nAll YAML files are valid!")
    else:
        print("\nSome YAML files have errors!")
