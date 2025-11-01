import os
import yaml
from dotenv import load_dotenv

def load_config(config_file):
    load_dotenv()
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    return {
        "api_base": os.getenv("API_BASE"),
        "api_key": os.getenv("API_KEY"),
        "models": config["models"]
    }
