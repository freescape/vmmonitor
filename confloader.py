import json
import os

class ConfigurationLoader:
   def __init__(self, path):
       self.path = path

   def load(self):
       try:
           with open(self.path, 'r') as f:
               config = json.load(f)
       except FileNotFoundError:
           raise ValueError(f"Configuration file at '{self.path}' not found")
       except json.JSONDecodeError:
           raise ValueError(f"Invalid JSON format in configuration file at '{self.path}'")
       
       self.validate( config )
       return config

   def validate(self, config):
       if 'listener' not in config or 'enabled' not in config['listener']:
           raise ValueError("Missing or invalid listener section in configuration")       
       if 'monitor' not in config or 'enabled' not in config['monitor']:
           raise ValueError("Missing or invalid monitor section in configuration")       
       if 'startup' not in config or 'enabled' not in config['startup']:
           raise ValueError("Missing or invalid startup section in configuration")       
       