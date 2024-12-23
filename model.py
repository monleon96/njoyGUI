import json
import os

class ModuleModel:
    def __init__(self, module_name):
        self.module_name = module_name
        self.description = ""
        self.cards = []

    def load_from_file(self, filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        self.module_name = data["name"]
        self.description = data.get("description", "")
        self.cards = data.get("cards", [])

def load_module(module_name):
    # Get the directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct absolute path to the modules directory
    modules_dir = os.path.join(current_dir, "modules")
    # Create full path to the module file
    filepath = os.path.join(modules_dir, f"{module_name.lower()}.json")
    model = ModuleModel(module_name)
    model.load_from_file(filepath)
    return model

def load_isotopes():
    filepath = "resources/isotopes.json"
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    return {}
