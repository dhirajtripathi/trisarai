from typing import Dict, Any, Optional
import os

class ConfigStore:
    _instance = None
    _config: Dict[str, Any] = {
        "llm_provider": "mock", # Default to mock
        "azure_config": {
            "api_key": "",
            "endpoint": "",
            "deployment": "",
            "model_name": "",
            "api_version": "2023-05-15"
        },
        "aws_config": {
            "region": "us-east-1",
            "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
            "access_key_id": "",
            "secret_access_key": ""
        },
        "google_config": {
            "api_key": "",
            "model": "gemini-1.5-pro"
        },
        "jira_config": {
            "url": "",
            "email": "",
            "api_token": "",
            "space_key": ""
        }
    }

    CONFIG_FILE = "config.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigStore, cls).__new__(cls)
            cls._instance._load_from_file()
        return cls._instance

    def _load_from_file(self):
        if os.path.exists(self.CONFIG_FILE):
             try:
                 import json
                 with open(self.CONFIG_FILE, "r") as f:
                     saved_config = json.load(f)
                     # Merge saved config into default to ensure new keys exist
                     self.update_config(saved_config)
                     print(f">>> [ConfigStore] Loaded config from {self.CONFIG_FILE}")
             except Exception as e:
                 print(f"!!! [ConfigStore] Failed to load config: {e}")

    def _save_to_file(self):
        import json
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self._config, f, indent=4)
            print(f">>> [ConfigStore] Saved config to {self.CONFIG_FILE}")
        except Exception as e:
             print(f"!!! [ConfigStore] Failed to save config: {e}")

    def get_config(self) -> Dict[str, Any]:
        return self._config

    def update_config(self, new_config: Dict[str, Any]):
        # Deep merge simplistic implementation
        for key, value in new_config.items():
            if key in self._config and isinstance(self._config[key], dict) and isinstance(value, dict):
                self._config[key].update(value)
            else:
                self._config[key] = value
        
        self._save_to_file()
        print(f">>> [ConfigStore] Updated Config: {self._config}")

    def get_llm_provider(self) -> str:
        return self._config.get("llm_provider", "mock")

    def get_azure_details(self):
        return self._config.get("azure_config", {})

    def get_aws_details(self):
        return self._config.get("aws_config", {})

    def get_google_details(self):
        return self._config.get("google_config", {})
