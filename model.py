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
    filepath = os.path.join("modules", f"{module_name}.json")
    model = ModuleModel(module_name)
    model.load_from_file(filepath)
    return model

def load_json_source(filepath):
    """Generic function to load any JSON source file"""
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    return {}
